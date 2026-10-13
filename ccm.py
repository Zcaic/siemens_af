import aerosandbox.numpy as anp
import aerosandbox as asb
from pathlib import Path
import subprocess

def ccm_createaf(afs: list[asb.Airfoil], afs_name: list[str], TE=False, guide_width=1.0, axis="z"):
    template = """
package macro;
import java.util.*;
import star.common.*;
import star.base.neo.*;
import star.cadmodeler.*;

public class ccm_createaf extends StarMacro {
  public void execute() {
    execute0();
  }
  private void execute0() {
    Simulation simulation_0 = getActiveSimulation();
    CadModel cadModel_0 = ((CadModel) simulation_0.get(SolidModelManager.class).getObject("3D-CAD Model 1"));
    simulation_0.get(SolidModelManager.class).editCadModel(cadModel_0);
    LabCoordinateSystem labCoordinateSystem_0 = simulation_0.getCoordinateSystemManager().getLabCoordinateSystem();

    List<double[][]> afs=new ArrayList<double[][]>(){{
        add(new double[][] {{xxx}}); \\ af_coords
    }}; 
    List<double[][]> guides=new ArrayList<double[][]>(){{
        add(new double[][] {{xxx}}); \\ af_guides
    }}; 
    String[] af_names={xxx}; \\af_names
    boolean TE=false; \\TE

    for (int i=0;i<afs.size();i++)
    {
        Sketch3D sketch3D_0 = cadModel_0.getFeatureManager().createSketch3D_2(labCoordinateSystem_0, true);
        sketch3D_0.setAutoPreview(true);
        cadModel_0.allowMakingPartDirty(false);
        cadModel_0.getFeatureManager().startSketch3DEdit(sketch3D_0);

        ArrayList<PointSketchPrimitive3DBase> pts= new ArrayList<PointSketchPrimitive3DBase>();
        for (double[] coord:afs.get(i)){
            PointSketchPrimitive3D pt = sketch3D_0.createPoint3DInternal(new DoubleVector(coord));
            pts.add(pt);
        }
        sketch3D_0.createSpline3D(pts, false);
        
        if(TE){
            LineSketchPrimitive3D te = sketch3D_0.createLine3D(pts.get(pts.size()-1),pts.get(0));
        }

        sketch3D_0.setApplyToAllInstances(false);
        sketch3D_0.setExcludedInstancedBodies(new ArrayList<>(Collections.<Body>emptyList()));
        sketch3D_0.setIsBodyGroupCreation(false);
        sketch3D_0.setAutoPreview(true);
        cadModel_0.getFeatureManager().markDependentNotUptodate(sketch3D_0);
        cadModel_0.allowMakingPartDirty(true);
        sketch3D_0.markFeatureForEdit();
        cadModel_0.allowMakingPartDirty(true);
        cadModel_0.getFeatureManager().stopSketch3DEdit(sketch3D_0, true);
        sketch3D_0.setIsUptoDate(true);
        cadModel_0.getFeatureManager().updateModelAfterFeatureEdited(sketch3D_0, null);
        // simulation_0.get(SolidModelManager.class).endEditCadModel(cadModel_0);
        sketch3D_0.setPresentationName(af_names[i]);


        Sketch3D sketch3D_1 = cadModel_0.getFeatureManager().createSketch3D_2(labCoordinateSystem_0, true);
        sketch3D_1.setAutoPreview(true);
        cadModel_0.allowMakingPartDirty(false);
        cadModel_0.getFeatureManager().startSketch3DEdit(sketch3D_1);

        double[][] guide_pts=guides.get(i);
        LineSketchPrimitive3D guide = sketch3D_1.createLine3D(new DoubleVector(guide_pts[0]),new DoubleVector(guide_pts[1]));
        
        sketch3D_1.setApplyToAllInstances(false);
        sketch3D_1.setExcludedInstancedBodies(new ArrayList<>(Collections.<Body>emptyList()));
        sketch3D_1.setIsBodyGroupCreation(false);
        sketch3D_1.setAutoPreview(true);
        cadModel_0.getFeatureManager().markDependentNotUptodate(sketch3D_1);
        cadModel_0.allowMakingPartDirty(true);
        sketch3D_1.markFeatureForEdit();
        cadModel_0.allowMakingPartDirty(true);
        cadModel_0.getFeatureManager().stopSketch3DEdit(sketch3D_1, true);
        sketch3D_1.setIsUptoDate(true);
        cadModel_0.getFeatureManager().updateModelAfterFeatureEdited(sketch3D_1, null);
        // simulation_0.get(SolidModelManager.class).endEditCadModel(cadModel_0);
        sketch3D_1.setPresentationName(String.format("%s_guide",af_names[i]));
    }
    simulation_0.get(SolidModelManager.class).endEditCadModel(cadModel_0);
  }
}
"""
    coords = []
    guides = []
    names = []
    for i in range(len(afs)):
        af = afs[i]
        coord = []
        for j in af.coordinates:
            if axis == "z":
                tmp = [str(j[0]), str(j[1]), "0.0"]
            else:
                tmp = [str(j[0]), "0.0", str(j[1])]
            tmp = ",".join(tmp)
            tmp = "{" + tmp + "}"
            coord.append(tmp)
        coord = ",".join(coord)
        coord = "{" + coord + "}"
        coord = f"add(new double[][] {coord});"
        coords.append(coord)

        le_idx = af.LE_index()
        le = af.coordinates[le_idx]
        if axis == "z":
            le = anp.array([le[0], le[1], 0.0])
            le_start = le - anp.array([0.0, 0.0, guide_width / 2.0])
            le_end = le + anp.array([0.0, 0.0, guide_width / 2.0])
        else:
            le = anp.array([le[0], 0.0, le[1]])
            le_start = le - anp.array([0.0, guide_width / 2.0, 0.0])
            le_end = le + anp.array([0.0, guide_width / 2.0, 0.0])
        le_start = map(str, le_start)
        le_start = ",".join(le_start)
        le_start = "{" + le_start + "}"
        le_end = map(str, le_end)
        le_end = ",".join(le_end)
        le_end = "{" + le_end + "}"
        guide = "{" + le_start + "," + le_end + "}"
        guide = f"add(new double[][] {guide});"
        guides.append(guide)

        name = f'"{afs_name[i]}"'
        names.append(name)

    coords = "\n\t\t\t\t".join(coords)
    guides = "\n\t\t\t\t".join(guides)
    names = ",".join(names)
    names = "{" + names + "}"
    te = "true" if TE else "false"

    template = template.replace("add(new double[][] {{xxx}}); \\ af_coords", coords)
    template = template.replace("add(new double[][] {{xxx}}); \\ af_guides", guides)
    template = template.replace("String[] af_names={xxx}; \\af_names", f"String[] af_names={names};")
    template = template.replace("boolean TE=false; \\TE", f"boolean TE={te};")

    runtime = Path("./runtime")
    runtime.mkdir(exist_ok=True)
    ccm_createaf = runtime / "ccm_createaf.java"
    ccm_createaf.write_text(template)


def ccm_modifyaf(afs: list[asb.Airfoil], afs_name: list[str], guide_width=1.0, axis="z"):
    template='''
package macro;
import java.util.*;
import star.common.*;
import star.base.neo.*;
import star.cadmodeler.*;

public class ccm_modifyaf extends StarMacro {
  public void execute() {
    execute0();
  }
  private void execute0() {
    Simulation simulation_0 = getActiveSimulation();
    CadModel cadModel_0 = ((CadModel) simulation_0.get(SolidModelManager.class).getObject("3D-CAD Model 1"));

    ArrayList<double[][]> coords=new ArrayList<double[][]>(){{
        add(new double[][] {{xxx}}); \\ coords
    }};
    ArrayList<double[][]> guides=new ArrayList<double[][]>(){{
        add(new double[][] {{xxx}}); \\ guide
    }};
    String[] afs_name={xxx}; \\ names

    for (int i=0;i<coords.size();i++)
    {
        Sketch3D sketch3D_0 = ((Sketch3D) cadModel_0.getFeature(afs_name[i]));
        sketch3D_0.setAutoPreview(true);
        cadModel_0.allowMakingPartDirty(false);
        // cadModel_0.getFeatureManager().updateModelForEditingFeature(sketch3D_0);
        cadModel_0.getFeatureManager().startSketch3DEdit(sketch3D_0);
        double[][] af_coord=coords.get(i);
        for(int j=0;j<af_coord.length;j++){
            PointSketchPrimitive3D pt = ((PointSketchPrimitive3D) sketch3D_0.getSketchPrimitive3D(String.format("Point %d",j+1)));
            // sketch3D_0.editPointLocal(pt, new DoubleVector(af_coord[j]));
            CoordinateInput coord=pt.getPointInput();
            coord.setVector0(af_coord[j][0]);
            coord.setVector1(af_coord[j][1]);
            coord.setVector2(af_coord[j][2]);
            pt.setPointInput(coord);
        }
        sketch3D_0.setApplyToAllInstances(false);
        sketch3D_0.setExcludedInstancedBodies(new ArrayList<>(Collections.<Body>emptyList()));
        sketch3D_0.setIsBodyGroupCreation(false);
        // sketch3D_0.setAutoPreview(true);
        cadModel_0.getFeatureManager().markDependentNotUptodate(sketch3D_0);
        cadModel_0.allowMakingPartDirty(true);
        sketch3D_0.markFeatureForEdit();
        cadModel_0.allowMakingPartDirty(true);
        cadModel_0.getFeatureManager().stopSketch3DEdit(sketch3D_0, false);
        cadModel_0.getFeatureManager().markDependentNotUptodate(sketch3D_0);
        // cadModel_0.getFeatureManager().updateModelAfterFeatureEdited(sketch3D_0, null);

        Sketch3D sketch3D_1 = ((Sketch3D) cadModel_0.getFeature(String.format("%s_guide",afs_name[i])));
        sketch3D_1.setAutoPreview(true);
        cadModel_0.allowMakingPartDirty(false);
        // cadModel_0.getFeatureManager().updateModelForEditingFeature(sketch3D_1);
        cadModel_0.getFeatureManager().startSketch3DEdit(sketch3D_1);
        double[][] guide_pts=guides.get(i);
        for (int j=0;j<guide_pts.length;j++){
            PointSketchPrimitive3D pt = ((PointSketchPrimitive3D) sketch3D_1.getSketchPrimitive3D(String.format("Point %d",j+1)));
            // sketch3D_1.editPointLocal(pt, new DoubleVector(guide_pts[j]));
            CoordinateInput coord=pt.getPointInput();
            coord.setVector0(guide_pts[j][0]);
            coord.setVector1(guide_pts[j][1]);
            coord.setVector2(guide_pts[j][2]);
            pt.setPointInput(coord);
        }
        sketch3D_1.setApplyToAllInstances(false);
        sketch3D_1.setExcludedInstancedBodies(new ArrayList<>(Collections.<Body>emptyList()));
        sketch3D_1.setIsBodyGroupCreation(false);
        sketch3D_1.setAutoPreview(true);
        cadModel_0.getFeatureManager().markDependentNotUptodate(sketch3D_1);
        cadModel_0.allowMakingPartDirty(true);
        sketch3D_1.markFeatureForEdit();
        cadModel_0.allowMakingPartDirty(true);
        cadModel_0.getFeatureManager().stopSketch3DEdit(sketch3D_1, false);
        cadModel_0.getFeatureManager().markDependentNotUptodate(sketch3D_1);
        // cadModel_0.getFeatureManager().updateModelAfterFeatureEdited(sketch3D_1, null);
    }
    cadModel_0.getFeatureManager().rollForwardToEnd(false);
    cadModel_0.update();
    simulation_0.get(SolidModelManager.class).endEditCadModel(cadModel_0);
  }
}
'''
    af_coords=[]
    af_names=[]
    af_guides=[]
    for i in range(len(afs)):
        coord=[]
        af=afs[i]
        for j in af.coordinates:
            if axis=="z":
                tmp=[str(j[0]),str(j[1]),"0.0"]
            else:
                tmp = [str(j[0]), "0.0", str(j[1])]
            tmp = ",".join(tmp)
            tmp = "{" + tmp + "}"
            coord.append(tmp)
        coord = ",".join(coord)
        coord = "{" + coord + "}"
        coord = f"add(new double[][] {coord});"
        af_coords.append(coord)

        le_idx = af.LE_index()
        le = af.coordinates[le_idx]
        if axis=="z":
            le = anp.array([le[0], le[1], 0.0])
            le_start = le - anp.array([0.0, 0.0, guide_width / 2.0])
            le_end = le + anp.array([0.0, 0.0, guide_width / 2.0])
        else:
            le = anp.array([le[0], 0.0, le[1]])
            le_start = le - anp.array([0.0, guide_width / 2.0, 0.0])
            le_end = le + anp.array([0.0, guide_width / 2.0, 0.0])     
        le_start = map(str, le_start)
        le_start = ",".join(le_start)
        le_start = "{" + le_start + "}"
        le_end = map(str, le_end)
        le_end = ",".join(le_end)
        le_end = "{" + le_end + "}"
        guide = "{" + le_start + "," + le_end + "}"
        guide = f"add(new double[][] {guide});"
        af_guides.append(guide)

        name = f'"{afs_name[i]}"'
        af_names.append(name)
    af_coords = "\n\t\t\t\t".join(af_coords)
    af_guides = "\n\t\t\t\t".join(af_guides)
    af_names = ",".join(af_names)
    af_names = "{" + af_names + "}"

    template = template.replace("add(new double[][] {{xxx}}); \\ coords",af_coords)
    template = template.replace("add(new double[][] {{xxx}}); \\ guide",af_guides)
    template = template.replace("String[] afs_name={xxx}; \\ names",f"String[] afs_name={af_names};")

    runtime = Path("./runtime")
    runtime.mkdir(exist_ok=True)
    ccm_createaf = runtime / "ccm_modifyaf.java"
    ccm_createaf.write_text(template)
    return ccm_createaf


def ccm_cfd(mach,alpha,pressure,temperature,density,outfile,clearsol=False,header=False,save=False,simname=None):
    template='''
package macro;

import java.util.*;
import java.io.FileWriter;
import java.io.PrintWriter;
import java.io.IOException;

import star.common.*;
import star.base.neo.*;
import star.base.report.*;
import star.flow.*;
import star.meshing.*;

public class %(script_fname)s extends StarMacro {

  @Override
  public void execute() {
    execute0();
  }

  private void execute0() {

    double aoa = %(aoa).6f;
    double mach = %(mach).6f;
    double pre0 = %(pre0).6f;
    double tem = %(tem).6f;
    double rho = %(rho).6f;
    String outfile = "%(outfile)s";
    boolean clearsol = %(clearsol)s;
    boolean outheader = %(outheader)s;
    boolean save = %(save)s;
    String simname = "%(simname)s"; 

    Simulation simulation_0 = getActiveSimulation();

    Units units_0 = ((Units) simulation_0.getUnitsManager().getObject("deg"));
    Units units_1 = ((Units) simulation_0.getUnitsManager().getObject(""));
    Units units_2 = ((Units) simulation_0.getUnitsManager().getObject("Pa"));
    Units units_3 = ((Units) simulation_0.getUnitsManager().getObject("K"));
    Units units_4 = ((Units) simulation_0.getUnitsManager().getObject("kg/m^3"));

    ScalarGlobalParameter P_aoa = ((ScalarGlobalParameter) simulation_0.get(GlobalParameterManager.class).getObject("AoA"));
    ScalarGlobalParameter P_ma = ((ScalarGlobalParameter) simulation_0.get(GlobalParameterManager.class).getObject("ma"));
    ScalarGlobalParameter P_pre0 = ((ScalarGlobalParameter) simulation_0.get(GlobalParameterManager.class).getObject("pre0"));
    ScalarGlobalParameter P_tem = ((ScalarGlobalParameter) simulation_0.get(GlobalParameterManager.class).getObject("tem"));
    ScalarGlobalParameter P_rho = ((ScalarGlobalParameter) simulation_0.get(GlobalParameterManager.class).getObject("rho"));

    P_aoa.getQuantity().setValueAndUnits(aoa, units_0);
    P_ma.getQuantity().setValueAndUnits(mach, units_1);
    P_pre0.getQuantity().setValueAndUnits(pre0, units_2);
    P_tem.getQuantity().setValueAndUnits(tem, units_3);
    P_rho.getQuantity().setValueAndUnits(rho, units_4);

    MeshPipelineController meshPipelineController_0 = simulation_0.get(MeshPipelineController.class);
    meshPipelineController_0.generateVolumeMesh();

    Solution solution_0 = simulation_0.getSolution();
    if(clearsol){
      solution_0.clearSolution(Solution.Clear.History, Solution.Clear.Fields, Solution.Clear.LagrangianDem);
    }
    

    simulation_0.getSimulationIterator().run();

    ForceReport report_lift = ((ForceReport) simulation_0.getReportManager().getReport("Lift"));
    double lift = report_lift.monitoredValue();

    ForceReport report_drag = ((ForceReport) simulation_0.getReportManager().getReport("Drag"));
    double drag = report_drag.monitoredValue();

    ExpressionReport report_ck = ((ExpressionReport) simulation_0.getReportManager().getReport("CK"));
    double ck = report_ck.monitoredValue();

    ForceCoefficientReport report_cl = ((ForceCoefficientReport) simulation_0.getReportManager().getReport("CL"));
    double cl = report_cl.monitoredValue();

    ForceCoefficientReport report_cd = ((ForceCoefficientReport) simulation_0.getReportManager().getReport("CD"));
    double cd = report_cd.monitoredValue();

    PrintWriter pw = null;
    try{
      FileWriter fw = new FileWriter(outfile,true);
      pw = new PrintWriter(fw);
    }catch(IOException e){
      e.printStackTrace();
    }

    String header = "pre,tem,rho,mach,alpha,Lift,Drag,CL,CD,CK";
    if (outheader){
      pw.println(header);
    }

    String data = String.format("%%.3f,%%.3f,%%.3f,%%.3f,%%.3f,%%.6f,%%.6f,%%.6f,%%.6f,%%.6f",pre0,tem,rho,mach,aoa,lift,drag,cl,cd,ck);
    pw.println(data);

    pw.close();

    if (save){
        simulation_0.saveState(simname, false);
    }
  }
}
'''

    cfd_script=Path("./runtime/ccm_cfd.java")
    cfd_script.parent.mkdir(exist_ok=True)
    script=template%{
        "script_fname":cfd_script.stem,
        "aoa":alpha,
        "mach":mach,
        "pre0":pressure,
        "tem":temperature,
        "rho":density,
        "outfile":Path(outfile).resolve().as_posix(),
        "clearsol":"true" if clearsol else "false",
        "outheader":"true" if header else "false",
        "save":"true" if save else "false",
        "simname":Path(simname).resolve().as_posix() if isinstance(simname,str) else " "
    }
    cfd_script.write_text(script)
    return cfd_script

def callstar(host,port,script:list[str],exe="starccm+",timeout=600):
    cmd=[exe,"-host",host+":"+port,"-batch",",".join(script),"-noexit"]
    try:
        p=subprocess.run(cmd,timeout=timeout,stdout=subprocess.DEVNULL)
    except subprocess.TimeoutExpired:
        print(f"=== \033[1;31m The maxumum runtime was exceeded!\033[0m ===")
    return p

if __name__ == "__main__":
    afs = []
    afs_name = []

    alpha=anp.arange(-2.0,8.0,2.0)

    af = asb.KulfanAirfoil("n63415").set_TE_thickness(2.4e-3).to_airfoil(n_coordinates_per_side=100)
    # af=asb.Airfoil("naca0012").set_TE_thickness(2.4e-3).to_kulfan_airfoil().to_airfoil(n_coordinates_per_side=100)

    af_name = f"af_0"
    afs.append(af)
    afs_name.append(af_name)
    
    for idx,i in enumerate(alpha):
        # ccm_createaf(afs=afs, afs_name=afs_name, TE=True)
        modify_script=ccm_modifyaf(afs=afs, afs_name=afs_name)
        cfd_script =ccm_cfd(mach=0.6,alpha=i,pressure=455217,temperature=220,density=0.66,outfile="./runtime/out.csv",clearsol=True,header=True if idx==0 else False,save=True,simname=f"./runtime/aoa_{i:.3f}.sim")

        callstar(host="DESKTOP-VRDCTE5",port="47827",script=[modify_script.resolve().as_posix(),cfd_script.resolve().as_posix()],timeout=6000)




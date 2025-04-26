import aerosandbox.numpy as anp
import aerosandbox as asb
from pathlib import Path


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
        simulation_0.get(SolidModelManager.class).endEditCadModel(cadModel_0);
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
        simulation_0.get(SolidModelManager.class).endEditCadModel(cadModel_0);
        sketch3D_1.setPresentationName(String.format("%s_guide",af_names[i]));
    }
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
        // sketch3D_0.setAutoPreview(true);
        cadModel_0.allowMakingPartDirty(false);
        // cadModel_0.getFeatureManager().updateModelForEditingFeature(sketch3D_0);
        cadModel_0.getFeatureManager().startSketch3DEdit(sketch3D_0);
        double[][] af_coord=coords.get(i);
        for(int j=0;j<af_coord.length;j++){
            PointSketchPrimitive3D pt = ((PointSketchPrimitive3D) sketch3D_0.getSketchPrimitive3D(String.format("Point %d",j+1)));
            sketch3D_0.editPointLocal(pt, new DoubleVector(af_coord[j]));
        }
        sketch3D_0.setApplyToAllInstances(false);
        // sketch3D_0.setExcludedInstancedBodies(new ArrayList<>(Collections.<Body>emptyList()));
        // sketch3D_0.setIsBodyGroupCreation(false);
        // sketch3D_0.setAutoPreview(true);
        cadModel_0.getFeatureManager().markDependentNotUptodate(sketch3D_0);
        cadModel_0.allowMakingPartDirty(true);
        sketch3D_0.markFeatureForEdit();
        cadModel_0.allowMakingPartDirty(true);
        cadModel_0.getFeatureManager().stopSketch3DEdit(sketch3D_0, false);
        cadModel_0.getFeatureManager().markDependentNotUptodate(sketch3D_0);
        // cadModel_0.getFeatureManager().updateModelAfterFeatureEdited(sketch3D_0, null);

        Sketch3D sketch3D_1 = ((Sketch3D) cadModel_0.getFeature(String.format("%s_guide",afs_name[i])));
        // sketch3D_1.setAutoPreview(true);
        cadModel_0.allowMakingPartDirty(false);
        // cadModel_0.getFeatureManager().updateModelForEditingFeature(sketch3D_1);
        cadModel_0.getFeatureManager().startSketch3DEdit(sketch3D_1);
        double[][] guide_pts=guides.get(i);
        for (int j=0;j<guide_pts.length;j++){
            PointSketchPrimitive3D pt = ((PointSketchPrimitive3D) sketch3D_1.getSketchPrimitive3D(String.format("Point %d",j+1)));
            sketch3D_1.editPointLocal(pt, new DoubleVector(guide_pts[j]));
        }
        sketch3D_1.setApplyToAllInstances(false);
        // sketch3D_1.setExcludedInstancedBodies(new ArrayList<>(Collections.<Body>emptyList()));
        // sketch3D_1.setIsBodyGroupCreation(false);
        // sketch3D_1.setAutoPreview(true);
        cadModel_0.getFeatureManager().markDependentNotUptodate(sketch3D_1);
        cadModel_0.allowMakingPartDirty(true);
        sketch3D_1.markFeatureForEdit();
        cadModel_0.allowMakingPartDirty(true);
        cadModel_0.getFeatureManager().stopSketch3DEdit(sketch3D_1, false);
        cadModel_0.getFeatureManager().markDependentNotUptodate(sketch3D_1);
        // cadModel_0.getFeatureManager().updateModelAfterFeatureEdited(sketch3D_1, null);
    }
    cadModel_0.update();
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

if __name__ == "__main__":
    afs = []
    afs_name = []

    for i in range(1):
        af = asb.KulfanAirfoil("n63415").to_airfoil(n_coordinates_per_side=100)
        af=af.scale(3.65,3.65).set_TE_thickness(2.4e-3)
        af_name = f"af_{i}"
        afs.append(af)
        afs_name.append(af_name)

    # ccm_createaf(afs=afs, afs_name=afs_name, TE=True)
    ccm_modifyaf(afs=afs, afs_name=afs_name)

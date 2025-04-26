// Simcenter STAR-CCM+ macro: test.java
// Written by Simcenter STAR-CCM+ 20.02.007
package macro;

import java.util.*;

import star.common.*;
import star.cadmodeler.*;

public class test extends StarMacro {

  public void execute() {
    execute0();
  }

  private void execute0() {

    Simulation simulation_0 = 
      getActiveSimulation();

    CadModel cadModel_0 = 
      ((CadModel) simulation_0.get(SolidModelManager.class).getObject("3D-CAD Model 1"));

    cadModel_0.update();
  }
}

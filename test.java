// Simcenter STAR-CCM+ macro: test.java
// Written by Simcenter STAR-CCM+ 21.04.008
package macro;

import java.util.*;

import star.common.*;
import star.base.neo.*;

public class test extends StarMacro {

  @Override
  public void execute() {
    execute0();
    // D:/Doc/siemens_af/star_Copy.sim
    execute1();
  }

  private void execute0() {

    Simulation simulation_0 = 
      getActiveSimulation();

    simulation_0.saveState("D:\\Doc\\siemens_af\\star_Copy.sim", false);
  }

  private void execute1() {
  }
}

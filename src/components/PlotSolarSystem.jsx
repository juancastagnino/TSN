import Pobj from "./Pobj";
import MoonOrbitalPlane from "./MoonOrbitalPlane";
import SunMarsBinarySystem from "./SunMarsBinarySystem";

const PlotSolarSystem = () => {
  return (
    <group>
      <Pobj name="SystemCenter">
      <Pobj name="Earth">
        <MoonOrbitalPlane>
          <Pobj name="Moon deferent A">
            <Pobj name="Moon" />
          </Pobj>
        </MoonOrbitalPlane>

          <SunMarsBinarySystem ObjectComponent={Pobj} plotMode />
        </Pobj>
      </Pobj>
    </group>
  );
};
export default PlotSolarSystem;

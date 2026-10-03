import React from "react";
import SunMarsBinarySystem from "./SunMarsBinarySystem";

const StubObject = () => null;

const childElements = (element) =>
  React.Children.toArray(element.props.children).filter(React.isValidElement);

const directChildNamed = (element, name) =>
  childElements(element).find((child) => child.props.name === name);

const descendantNames = (element) => {
  const names = [];

  const visit = (node) => {
    if (!React.isValidElement(node)) return;
    if (node.props.name) names.push(node.props.name);
    childElements(node).forEach(visit);
  };

  visit(element);
  return names;
};

test("models the Sun and Mars as sibling companion branches", () => {
  const binaryFrame = SunMarsBinarySystem({ ObjectComponent: StubObject });
  const sunBranch = directChildNamed(binaryFrame, "Sun Companion Branch");
  const marsBranch = directChildNamed(binaryFrame, "Mars Companion Branch");

  expect(binaryFrame.props.name).toBe("Sun-Mars Binary Frame");
  expect(sunBranch).toBeDefined();
  expect(marsBranch).toBeDefined();
  expect(descendantNames(sunBranch)).toContain("Sun");
  expect(descendantNames(sunBranch)).not.toContain("Mars");
  expect(descendantNames(marsBranch)).toContain("Mars");
  expect(descendantNames(marsBranch)).not.toContain("Sun");
});

test("keeps each companion's moons in its own named branch", () => {
  const binaryFrame = SunMarsBinarySystem({ ObjectComponent: StubObject });
  const solarMoonBranches = directChildNamed(
    binaryFrame,
    "Solar Moon Carrier Branches"
  );
  const marsBranch = directChildNamed(binaryFrame, "Mars Companion Branch");

  expect(descendantNames(solarMoonBranches)).toEqual(
    expect.arrayContaining(["Mercury", "Venus"])
  );
  expect(descendantNames(marsBranch)).toEqual(
    expect.arrayContaining(["Phobos", "Deimos"])
  );
});

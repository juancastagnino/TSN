import { movePlotModel } from "./plotModelFunctions";

test("settles negative-priority geometry before dependent plot adapters", () => {
  const calls = [];
  const plotObjects = [
    {
      name: "dependent",
      updateAfterMotion: () => calls.push("dependent"),
    },
    {
      name: "early geometry",
      updatePriority: -1,
      updateAfterMotion: () => calls.push("early geometry"),
    },
    {
      name: "later dependent",
      updateAfterMotion: () => calls.push("later dependent"),
    },
  ];

  movePlotModel(plotObjects, 0);
  expect(calls).toEqual(["early geometry", "dependent", "later dependent"]);
});

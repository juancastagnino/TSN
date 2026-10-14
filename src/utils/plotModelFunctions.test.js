import { movePlotModel } from "./plotModelFunctions";

test("settles negative-priority geometry before dependent plot adapters", () => {
  const calls = [];
  const plotObjects = [
    {
      name: "dependent",
      updateAfterMotion: () => calls.push("dependent"),
    },
    {
      name: "equant",
      updatePriority: -1,
      updateAfterMotion: () => calls.push("equant"),
    },
    {
      name: "later dependent",
      updateAfterMotion: () => calls.push("later dependent"),
    },
  ];

  movePlotModel(plotObjects, 0);
  expect(calls).toEqual(["equant", "dependent", "later dependent"]);
});

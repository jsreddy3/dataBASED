import React from "react";
import SuggestedFields from "./SuggestedFields";
import SelectedFields from "./SelectedFields";

const DragDropList = ({ suggested, selected, onDragEnd }) => {
  return (
    <>
      <SuggestedFields items={suggested} onDrop={onDragEnd} />
      <SelectedFields items={selected} />
    </>
  );
};

export default DragDropList;
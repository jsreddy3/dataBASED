// import React from 'react';

// const SuggestedFields = ({ items, onFieldAction }) => {
//   return (
//     <div>
//       {items.map((item, index) => (
//         <div key={item.id} style={{ display: "flex", alignItems: "center" }}>
//           <div style={{ marginRight: "10px" }}>{item.name}</div>
//           <button onClick={() => onFieldAction(item.id, "select")}>Select</button>
//           <button onClick={() => onFieldAction(item.id, "reject")}>Reject</button>
//         </div>
//       ))}
//     </div>
//   );
// };

// export default SuggestedFields;

import React from "react";
import { Button, useTheme } from "@mui/material";
import { tokens } from "./../theme";

const SuggestedFields = ({ items, onFieldAction }) => {
  const theme = useTheme();
  const colors = tokens(theme.palette.mode);
  const selectButtonTextColor = colors.grey[100];
  const selectButtonBackgroundColor = colors.greenAccent[600];
  const rejectButtonTextColor = colors.grey[100];
  const rejectButtonBackgroundColor = colors.redAccent[400];

  return (
    <div>
      {items.map((item, index) => (
        <div
          key={item.id}
          style={{
            display: "flex",
            alignItems: "center",
            marginBottom: "10px",
          }}
        >
          <div style={{ marginRight: "10px", flexGrow: 1 }}>{item.name}</div>
          <Button
            variant="contained"
            style={{
              backgroundColor: selectButtonBackgroundColor,
              color: selectButtonTextColor,
              marginRight: "10px",
            }}
            onClick={() => onFieldAction(item.id, "select")}
          >
            Select
          </Button>
          <Button
            variant="contained"
            style={{
              backgroundColor: rejectButtonBackgroundColor,
              color: rejectButtonTextColor,
              marginRight: "10px",
            }}
            onClick={() => onFieldAction(item.id, "reject")}
          >
            Reject
          </Button>
        </div>
      ))}
    </div>
  );
};

export default SuggestedFields;

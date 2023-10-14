// import React from 'react';

// const SelectedFields = ({ items, onUnselect }) => {
//   const handleUnselectClick = (itemId) => {
//     onUnselect(itemId);
//   };

//   return (
//     <div>
//       {items.map((item, index) => (
//         <div key={item.id} style={{ display: "flex", alignItems: "center" }}>
//           <div style={{ marginRight: "10px" }}>{item.name}</div>
//           <button onClick={() => handleUnselectClick(item.id)}>Unselect</button>
//         </div>
//       ))}
//     </div>
//   );
// };

// export default SelectedFields;

import React from "react";
import { Button, useTheme } from "@mui/material";
import { tokens } from "./../theme";

const SelectedFields = ({ items, onUnselect }) => {
  const handleUnselectClick = (itemId) => {
    onUnselect(itemId);
  };
  const theme = useTheme();
  const colors = tokens(theme.palette.mode);
  const buttonTextcolor = colors.grey[100];
  const buttonBackgroundcolor = colors.primary[400];

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
              backgroundColor: buttonBackgroundcolor,
              color: buttonTextcolor,
              marginRight: "10px",
            }}
            onClick={() => handleUnselectClick(item.id)}
          >
            Unselect
          </Button>
        </div>
      ))}
    </div>
  );
};

export default SelectedFields;

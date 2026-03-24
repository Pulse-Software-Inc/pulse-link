{
  /* Button that takes you to a different page */
}

import React from 'react';
import { Button } from "@mui/material";
import Link from "next/link";

export default function LinkButton(props) {
  return (
    <Link href={props.link}>
      <Button
        variant="contained"
        sx={{
          background: "#E1B3F6",
          borderRadius: props.borderRadius,
          paddingX: props.px,
          paddingY: props.py,
          fontSize: props.fsize,
          fontWeight: props.fweight,
          textTransform: "none",
          boxShadow: "0 10px 15px -3px rgba(0, 0, 0, 0.1)",
          "&:hover": {
            background: "#d09ff0",
            boxShadow: "0 20px 25px -5px rgba(0, 0, 0, 0.1)",
          }
        }}
      >
        {props.text}
      </Button>
    </Link>
  );
}

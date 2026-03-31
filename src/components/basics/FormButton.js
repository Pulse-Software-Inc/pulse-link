{
  /* Styled Button that submits a form */
}

import React from 'react';

export default function LinkButton(props) {
  return (
    <button
      type="submit"
      className="w-full py-3 text-sm font-semibold text-white rounded-xl shadow-md mt-2 transition-colors bg-[#D7B2FF] hover:bg-[#C89EFF]"
    >
      {props.text}
    </button>
  );
}

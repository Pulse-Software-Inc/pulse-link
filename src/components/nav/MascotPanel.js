'use client';

import React from 'react';
import Image from 'next/image';

function clampPct(x) {
  const n=Number(x);
  if(!Number.isFinite(n)) return 0;
  return Math.max(0,Math.min(100,n));
}
function pickMascot(stepsPct,caloriesPct) {
  const s=clampPct(stepsPct);
  const c=clampPct(caloriesPct);
  const score=(s+c)/ 2;

  if (score <25) return '/Mascot/pulseydevastated.png';
  if (score <50) return '/Mascot/pulseygym.png';
  if (score <75) return '/Mascot/pulseymeow.png';
  return '/Mascot/pulseyhappy.png';
}
export default function MascotPanel({ stepsPct = 0, caloriesPct = 0 }) {
  const src = pickMascot(stepsPct, caloriesPct);

  return (
    <div className="rounded-2xl bg-white flex items-center justify-center h-full w-full">
      <Image
        src={src}
        alt="Mascot"
        width={520}
        height={900}
        className="w-full max-w-[420px] h-auto object-contain"
        priority
      />
    </div>
  );
}
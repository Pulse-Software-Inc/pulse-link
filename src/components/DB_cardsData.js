'use client';

//using this file for the data going to be used in the DB cards. 
const DB_cardsData = [
    {
        id: "Steps",
        title: "Steps",
        iconSrc: "/Steps_Icon.svg",
        main: "11,200",
        sub: "/10,000",
        footer: "12% more than yesterday",
        progress: { value: 11200, max: 10000 },
    },
    {
        id: "Kcal",
        title: "Calories Burned",
        iconSrc: "Calories_Icon.svg",
        main: "435",
        sub: "/500",
        footer: null,
        progress: { value: 435, max: 500 },
    },
    {
        id: "Heart",
        title: "Heart Rate",
        iconSrc: "/HeartRate_Icon.svg",
        main: "74",
        sub: "BPM",
        footer: "Resting: 68 BPM | Synced: 2 mins ago",
        progress: null,
    },
];

export default DB_cardsData;


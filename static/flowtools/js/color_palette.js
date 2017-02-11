// Copyright (c) 2016 Northrop Grumman.
// All rights reserved.

var color_palette = [
  '#000000', // Black 0
  '#FF0000', // Red 1
  '#FFFF00', // Yellow 2
  '#008000', // Dark Green 3
  '#0000FF', // Blue 4
  '#FFA500', // Orange 5
  '#8A2BE2', // BlueViolet 6
  '#808000', // Olive 7
  '#00FFFF', // Cyan 8
  '#FF00FF', // Magenta 9
  '#00FF00', // Green 10
  '#000080', // Navy Blue 11
  '#F08080', // Light Coral 12
  '#800080', // Purple 13
  '#F0E68C', // Khaki 14
  '#8FBC8F', // Dark Sea Green 15
  '#2F4F4F', // Dark Slate Grey 16
  '#008080', // Teal 17
  '#9932CC', // Dark Orchid 18
  '#FF7F50', // Coral 19
  '#FFD700', // Gold 20
  '#008B8B', // Cyan 4 21
  '#800000', // Maroon 22
  '#5F9EA0', // Cadet Blue 23
  '#FFC0CB', // Pink 24
  '#545454', // Grey 25
  '#7FFFD4', // Aquamarine 26
  '#ADD8E6', // Light Blue 27
  '#DB7093', // Medium Violet Red 28
  '#CD853F', // Tan 3 29
  '#4169E1', // Royal Blue 30
  '#708090', // Slate Grey 31
  '#4682B4', // Steel Blue 32
  '#D8BFD8', // Thistle 33
  '#F5DEB3', // Wheat 34
  '#9ACD32', // Yellow Green 35
  '#BDB76B', // Dark Khaki 36
  '#8B008B', // Magenta 4 37
  '#556B2F', // Dark Olive Green 38
  '#00CED1', // Dark Turquoise 39
  '#FF1493' // Deep Pink
]

var rgb_palette = [
  'rgba(0,0,0,', // Black 0
  'rgba(255,0,0,', // Red 1
  'rgba(255,255,0,', // Yellow 2
  'rgba(0,128,0,', // Dark Green 3
  'rgba(0,0,255,', // Blue 4
  'rgba(255,165,0,', // Orange 5
  'rgba(138,43,226,', // BlueViolet 6
  'rgba(128,128,0,', // Olive 7
  'rgba(0,255,255,', // Cyan 8
  'rgba(255,0,255,', // Magenta 9
  'rgba(0,255,0,', // Green 10
  'rgba(0,0,128,', // Navy Blue 11
  'rgba(240,128,128,', // Light Coral 12
  'rgba(128,0,128,', // Purple 13
  'rgba(240,230,140,', // Khaki 14
  'rgba(143,188,143,', // Dark Sea Green 15
  'rgba(47,79,79,', // Dark Slate Grey 16
  'rgba(0,128,128,', // Teal 17
  'rgba(153,50,204,', // Dark Orchid 18
  'rgba(255,127,80,', // Coral 19
  'rgba(255,215,0,', // Gold 20
  'rgba(0,139,139,', // Cyan 4 21
  'rgba(128,0,0,', // Maroon 22
  'rgba(95,158,160,', // Cadet Blue 23
  'rgba(255,192,203,', // Pink 24
  'rgba(84,84,84,', // Grey 25
  'rgba(127,255,212,', // Aquamarine 26
  'rgba(173,216,230,', // Light Blue 27
  'rgba(219,112,147,', // Medium Violet Red 28
  'rgba(205,133,63,', // Tan 3 29
  'rgba(65,105,225,', // Royal Blue 30
  'rgba(112,128,144,', // Slate Grey 31
  'rgba(70,130,180,', // Steel Blue 32
  'rgba(216,191,216,', // Thistle 33
  'rgba(245,222,179,', // Wheat 34
  'rgba(154,205,50,', // Yellow Green 35
  'rgba(189,183,107,', // Dark Khaki 36
  'rgba(139,0,139,', // Magenta 4 37
  'rgba(85,107,47,', // Dark Olive Green 38
  'rgba(0,206,209,', // Dark Turquoise 39
  'rgba(255,20,147,' // Deep Pink
]

/* Standing out palette to display additional info like MFI bar on boxplot
** A lot of them will be the same but the goal is to have the same structure
** to use when plotting than above, while keeping this palette restricted to
** as few colors as possible standing out over black, white and whatever color
** they will be overlaid on.
*/
var so_palette = [
  'rgba(255,0,0,', // Black 0 --> red
  'rgba(52,17,81,', // Red 1 -->  dark purple
  'rgba(52,17,81,', // Yellow 2 --> dark purple
  'rgba(52,17,81,', // Dark Green 3 --> dark purple
  'rgba(255,0,0,', // Blue 4 --> red
  'rgba(52,17,81,', // Orange 5 --> dark purple
  'rgba(52,17,81,', // BlueViolet 6 --> dark purple
  'rgba(52,17,81,', // Olive 7 --> dark purple
  'rgba(52,17,81,', // Cyan 8 --> dark purple
  'rgba(52,17,81,', // Magenta 9 --> dark purple
  'rgba(52,17,81,', // Green 10 --> dark purple
  'rgba(255,0,0,', // Navy Blue 11 --> red
  'rgba(52,17,81,', // Light Coral 12 --> dark purple
  'rgba(255,0,0,', // Purple 13 --> red
  'rgba(52,17,81,', // Khaki 14 --> dark purple
  'rgba(52,17,81,', // Dark Sea Green 15 --> dark purple
  'rgba(52,17,81,', // Dark Slate Grey 16 --> dark purple
  'rgba(52,17,81,', // Teal 17 --> dark purple
  'rgba(52,17,81,', // Dark Orchid 18 --> dark purple
  'rgba(52,17,81,', // Coral 19  --> dark purple
  'rgba(52,17,81,', // Gold 20 --> dark purple
  'rgba(52,17,81,', // Cyan 4 21 --> dark purple
  'rgba(255,0,0,', // Maroon 22 --> red
  'rgba(52,17,81,', // Cadet Blue 23 --> dark purple
  'rgba(52,17,81,', // Pink 24 --> red
  'rgba(255,0,0,', // Grey 25 --> red
  'rgba(255,0,0,', // Aquamarine 26 --> red
  'rgba(52,17,81,', // Light Blue 27 --> dark purple
  'rgba(52,17,81,', // Medium Violet Red 28 --> dark purple
  'rgba(52,17,81,', // Tan 3 29 --> dark purple
  'rgba(52,17,81,', // Royal Blue 30 --> dark purple
  'rgba(52,17,81,', // Slate Grey 31 --> dark purple
  'rgba(52,17,81,', // Steel Blue 32 --> dark purple
  'rgba(52,17,81,', // Thistle 33 --> dark purple
  'rgba(52,17,81,', // Wheat 34 --> dark purple
  'rgba(52,17,81,', // Yellow Green 35 --> dark purple
  'rgba(52,17,81,', // Dark Khaki 36 --> dark purple
  'rgba(255,0,0,', // Magenta 4 37 --> red
  'rgba(52,17,81,', // Dark Olive Green 38 --> dark purple
  'rgba(52,17,81,', // Dark Turquoise 39 --> dark purple
  'rgba(52,17,81,' // Deep Pink --> dark purple
]

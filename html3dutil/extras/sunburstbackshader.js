/** The <code>extras/sunburstbackshader.js</code> module.
 * To import all symbols in this module, either of the following can be used:
 * <pre>
 * import * from "extras/sunburstbackshader.js";
 * // -- or --
 * import * as CustomModuleName from "extras/sunburstbackshader.js";</pre>
 * @module extras/sunburstbackshader */
/** The <code>extras/sunburstbackshader.js</code> module.
 * To import all symbols in this module, either of the following can be used:
 * <pre>
 * import * from "extras/sunburstbackshader.js";
 * // -- or --;
 * import * as CustomModuleName from "extras/sunburstbackshader.js";
 * @module extras/sunburstbackshader */

/*
 Any copyright to this file is released to the Public Domain.
 http://creativecommons.org/publicdomain/zero/1.0/
 If you like this, you should donate
 to Peter O. (original author of
 the Public Domain HTML 3D Library) at:
 http://peteroupc.github.io/
*/

/**
 * TODO: Not documented yet.
 */
export var sunburstBackShader = {
  "uniform":{
    "blackColor":[0, 0, 0],
    "whiteColor":[1, 1, 1],
    "time":0
  },
  "vertexShader":[
    "varying vec2 posVar;",
    "void main() {",
    " posVar=position.xy;",
    " gl_Position=vec4(position,1.0);",
    "}"].join("\n"),
  "fragmentShader":[
    "uniform vec3 blackColor;",
    "uniform vec3 whiteColor;",
    "varying vec2 posVar;",
    "uniform float time;",
    "void main() {",
    " float angle=atan(posVar.y,posVar.x);",
    " angle/=6.283185307;",
    " angle=mod(angle+time*0.001,1.0); // Time range is [0,1000)",
    " angle=floor(angle*24.0);",
    " float s=(mod(angle,2.0)>=1.0) ? 1.0 : 0.0;",
    " vec3 color=mix(blackColor,whiteColor,s);",
    " gl_FragColor=vec4(color,1.0);",
    "}"].join("\n")
};

(self.webpackJsonp=self.webpackJsonp||[]).push([[68],{204:function(e,t,r){"use strict";var n=r(219);r.d(t,"a",function(){return i});const i=Object(n.a)({types:{"entity-id":function(e){return"string"!=typeof e?"entity id should be a string":!!e.includes(".")||"entity id should be in the format 'domain.entity'"},icon:function(e){return"string"!=typeof e?"icon should be a string":!!e.includes(":")||"icon should be in the format 'mdi:icon'"}}})},219:function(e,t,r){"use strict";r.d(t,"a",function(){return _});class n extends TypeError{static format(e){const{type:t,path:r,value:n}=e;return`Expected a value of type \`${t}\`${r.length?` for \`${r.join(".")}\``:""} but received \`${JSON.stringify(n)}\`.`}constructor(e){super(n.format(e));const{data:t,path:r,value:i,reason:o,type:a,errors:s=[]}=e;this.data=t,this.path=r,this.value=i,this.reason=o,this.type=a,this.errors=s,s.length||s.push(this),Error.captureStackTrace?Error.captureStackTrace(this,this.constructor):this.stack=(new Error).stack}}var i=Object.prototype.toString,o=function(e){if(void 0===e)return"undefined";if(null===e)return"null";var t=typeof e;if("boolean"===t)return"boolean";if("string"===t)return"string";if("number"===t)return"number";if("symbol"===t)return"symbol";if("function"===t)return"GeneratorFunction"===a(e)?"generatorfunction":"function";if(function(e){return Array.isArray?Array.isArray(e):e instanceof Array}(e))return"array";if(function(e){if(e.constructor&&"function"==typeof e.constructor.isBuffer)return e.constructor.isBuffer(e);return!1}(e))return"buffer";if(function(e){try{if("number"==typeof e.length&&"function"==typeof e.callee)return!0}catch(t){if(-1!==t.message.indexOf("callee"))return!0}return!1}(e))return"arguments";if(function(e){return e instanceof Date||"function"==typeof e.toDateString&&"function"==typeof e.getDate&&"function"==typeof e.setDate}(e))return"date";if(function(e){return e instanceof Error||"string"==typeof e.message&&e.constructor&&"number"==typeof e.constructor.stackTraceLimit}(e))return"error";if(function(e){return e instanceof RegExp||"string"==typeof e.flags&&"boolean"==typeof e.ignoreCase&&"boolean"==typeof e.multiline&&"boolean"==typeof e.global}(e))return"regexp";switch(a(e)){case"Symbol":return"symbol";case"Promise":return"promise";case"WeakMap":return"weakmap";case"WeakSet":return"weakset";case"Map":return"map";case"Set":return"set";case"Int8Array":return"int8array";case"Uint8Array":return"uint8array";case"Uint8ClampedArray":return"uint8clampedarray";case"Int16Array":return"int16array";case"Uint16Array":return"uint16array";case"Int32Array":return"int32array";case"Uint32Array":return"uint32array";case"Float32Array":return"float32array";case"Float64Array":return"float64array"}if(function(e){return"function"==typeof e.throw&&"function"==typeof e.return&&"function"==typeof e.next}(e))return"generator";switch(t=i.call(e)){case"[object Object]":return"object";case"[object Map Iterator]":return"mapiterator";case"[object Set Iterator]":return"setiterator";case"[object String Iterator]":return"stringiterator";case"[object Array Iterator]":return"arrayiterator"}return t.slice(8,-1).toLowerCase().replace(/\s/g,"")};function a(e){return e.constructor?e.constructor.name:null}const s="@@__STRUCT__@@",c="@@__KIND__@@";function u(e){return!(!e||!e[s])}function l(e,t){return"function"==typeof e?e(t):e}var f=Object.assign||function(e){for(var t=1;t<arguments.length;t++){var r=arguments[t];for(var n in r)Object.prototype.hasOwnProperty.call(r,n)&&(e[n]=r[n])}return e};class d{constructor(e,t,r){this.name=e,this.type=t,this.validate=r}}function p(e,t,r){if(u(e))return e[c];if(e instanceof d)return e;switch(o(e)){case"array":return e.length>1?b(e,t,r):v(e,t,r);case"function":return y(e,t,r);case"object":return m(e,t,r);case"string":{let n,i=!0;if(e.endsWith("?")&&(i=!1,e=e.slice(0,-1)),e.includes("|")){n=k(e.split(/\s*\|\s*/g),t,r)}else if(e.includes("&")){n=E(e.split(/\s*&\s*/g),t,r)}else n=w(e,t,r);return i||(n=g(n,void 0,r)),n}}throw new Error(`Invalid schema: ${e}`)}function h(e,t,r){if("array"!==o(e))throw new Error(`Invalid schema: ${e}`);const n=e.map(e=>{try{return JSON.stringify(e)}catch(t){return String(e)}}).join(" | ");return new d("enum",n,(r=l(t))=>e.includes(r)?[void 0,r]:[{data:r,path:[],value:r,type:n}])}function y(e,t,r){if("function"!==o(e))throw new Error(`Invalid schema: ${e}`);return new d("function","<function>",(r=l(t),n)=>{const i=e(r,n);let a,s={path:[],reason:null};switch(o(i)){case"boolean":a=i;break;case"string":a=!1,s.reason=i;break;case"object":a=!1,s=f({},s,i);break;default:throw new Error(`Invalid result: ${i}`)}return a?[void 0,r]:[f({type:"<function>",value:r,data:r},s)]})}function v(e,t,r){if("array"!==o(e)||1!==e.length)throw new Error(`Invalid schema: ${e}`);const n=w("array",void 0,r),i=p(e[0],void 0,r),a=`[${i.type}]`;return new d("list",a,(e=l(t))=>{const[r,o]=n.validate(e);if(r)return r.type=a,[r];e=o;const s=[],c=[];for(let t=0;t<e.length;t++){const r=e[t],[n,o]=i.validate(r);n?(n.errors||[n]).forEach(r=>{r.path=[t].concat(r.path),r.data=e,s.push(r)}):c[t]=o}if(s.length){const e=s[0];return e.errors=s,[e]}return[void 0,c]})}function m(e,t,r){if("object"!==o(e))throw new Error(`Invalid schema: ${e}`);const n=w("object",void 0,r),i=[],a={};for(const o in e){i.push(o);const t=p(e[o],void 0,r);a[o]=t}const s=`{${i.join()}}`;return new d("object",s,(e=l(t))=>{const[r]=n.validate(e);if(r)return r.type=s,[r];const i=[],o={},c=Object.keys(e),u=Object.keys(a);if(new Set(c.concat(u)).forEach(r=>{let n=e[r];const s=a[r];if(void 0===n&&(n=l(t&&t[r],e)),!s){const t={data:e,path:[r],value:n};return void i.push(t)}const[c,u]=s.validate(n,e);c?(c.errors||[c]).forEach(t=>{t.path=[r].concat(t.path),t.data=e,i.push(t)}):(r in e||void 0!==u)&&(o[r]=u)}),i.length){const e=i[0];return e.errors=i,[e]}return[void 0,o]})}function g(e,t,r){return k([e,"undefined"],t,r)}function w(e,t,r){if("string"!==o(e))throw new Error(`Invalid schema: ${e}`);const{types:n}=r,i=n[e];if("function"!==o(i))throw new Error(`Invalid type: ${e}`);const a=y(i,t),s=e;return new d("scalar",s,e=>{const[t,r]=a.validate(e);return t?(t.type=s,[t]):[void 0,r]})}function b(e,t,r){if("array"!==o(e))throw new Error(`Invalid schema: ${e}`);const n=e.map(e=>p(e,void 0,r)),i=w("array",void 0,r),a=`[${n.map(e=>e.type).join()}]`;return new d("tuple",a,(e=l(t))=>{const[r]=i.validate(e);if(r)return r.type=a,[r];const o=[],s=[],c=Math.max(e.length,n.length);for(let t=0;t<c;t++){const r=n[t],i=e[t];if(!r){const r={data:e,path:[t],value:i};s.push(r);continue}const[a,c]=r.validate(i);a?(a.errors||[a]).forEach(r=>{r.path=[t].concat(r.path),r.data=e,s.push(r)}):o[t]=c}if(s.length){const e=s[0];return e.errors=s,[e]}return[void 0,o]})}function k(e,t,r){if("array"!==o(e))throw new Error(`Invalid schema: ${e}`);const n=e.map(e=>p(e,void 0,r)),i=n.map(e=>e.type).join(" | ");return new d("union",i,(e=l(t))=>{const r=[];for(const t of n){const[n,i]=t.validate(e);if(!n)return[void 0,i];r.push(n)}return r[0].type=i,r})}function E(e,t,r){if("array"!==o(e))throw new Error(`Invalid schema: ${e}`);const n=e.map(e=>p(e,void 0,r)),i=n.map(e=>e.type).join(" & ");return new d("intersection",i,(e=l(t))=>{let r=e;for(const t of n){const[e,n]=t.validate(r);if(e)return e.type=i,[e];r=n}return[void 0,r]})}const j={any:p,dict:function(e,t,r){if("array"!==o(e)||2!==e.length)throw new Error(`Invalid schema: ${e}`);const n=w("object",void 0,r),i=p(e[0],void 0,r),a=p(e[1],void 0,r),s=`dict<${i.type},${a.type}>`;return new d("dict",s,e=>{const r=l(t);e=r?f({},r,e):e;const[o]=n.validate(e);if(o)return o.type=s,[o];const c={},u=[];for(let t in e){const r=e[t],[n,o]=i.validate(t);if(n){(n.errors||[n]).forEach(r=>{r.path=[t].concat(r.path),r.data=e,u.push(r)});continue}t=o;const[s,l]=a.validate(r);s?(s.errors||[s]).forEach(r=>{r.path=[t].concat(r.path),r.data=e,u.push(r)}):c[t]=l}if(u.length){const e=u[0];return e.errors=u,[e]}return[void 0,c]})},enum:h,enums:function(e,t,r){return v([h(e,void 0)],t,r)},function:y,instance:function(e,t,r){const n=`instance<${e.name}>`;return new d("instance",n,(r=l(t))=>r instanceof e?[void 0,r]:[{data:r,path:[],value:r,type:n}])},interface:function(e,t,r){if("object"!==o(e))throw new Error(`Invalid schema: ${e}`);const n=[],i={};for(const o in e){n.push(o);const t=p(e[o],void 0,r);i[o]=t}const a=`{${n.join()}}`;return new d("interface",a,e=>{const r=l(t);e=r?f({},r,e):e;const n=[],o=e;for(const a in i){let r=e[a];const s=i[a];void 0===r&&(r=l(t&&t[a],e));const[c,u]=s.validate(r,e);c?(c.errors||[c]).forEach(t=>{t.path=[a].concat(t.path),t.data=e,n.push(t)}):(a in e||void 0!==u)&&(o[a]=u)}if(n.length){const e=n[0];return e.errors=n,[e]}return[void 0,o]})},lazy:function(e,t,r){if("function"!==o(e))throw new Error(`Invalid schema: ${e}`);let n,i;return n=new d("lazy","lazy...",t=>(i=e(),n.name=i.kind,n.type=i.type,n.validate=i.validate,n.validate(t)))},list:v,literal:function(e,t,r){const n=`literal: ${JSON.stringify(e)}`;return new d("literal",n,(r=l(t))=>r===e?[void 0,r]:[{data:r,path:[],value:r,type:n}])},object:m,optional:g,partial:function(e,t,r){if("object"!==o(e))throw new Error(`Invalid schema: ${e}`);const n=w("object",void 0,r),i=[],a={};for(const o in e){i.push(o);const t=p(e[o],void 0,r);a[o]=t}const s=`{${i.join()},...}`;return new d("partial",s,(e=l(t))=>{const[r]=n.validate(e);if(r)return r.type=s,[r];const i=[],o={};for(const n in a){let r=e[n];const s=a[n];void 0===r&&(r=l(t&&t[n],e));const[c,u]=s.validate(r,e);c?(c.errors||[c]).forEach(t=>{t.path=[n].concat(t.path),t.data=e,i.push(t)}):(n in e||void 0!==u)&&(o[n]=u)}if(i.length){const e=i[0];return e.errors=i,[e]}return[void 0,o]})},scalar:w,tuple:b,union:k,intersection:E,dynamic:function(e,t,r){if("function"!==o(e))throw new Error(`Invalid schema: ${e}`);return new d("dynamic","dynamic...",(r=l(t),n)=>{const i=e(r,n);if("function"!==o(i))throw new Error(`Invalid schema: ${i}`);const[a,s]=i.validate(r);return a?[a]:[void 0,s]})}},$={any:e=>void 0!==e};function _(e={}){const t=f({},$,e.types||{});function r(e,r,i={}){u(e)&&(e=e.schema);const o=j.any(e,r,f({},i,{types:t}));function a(e){if(this instanceof a)throw new Error("Invalid `new` keyword!");return a.assert(e)}return Object.defineProperty(a,s,{value:!0}),Object.defineProperty(a,c,{value:o}),a.kind=o.name,a.type=o.type,a.schema=e,a.defaults=r,a.options=i,a.assert=(e=>{const[t,r]=o.validate(e);if(t)throw new n(t);return r}),a.test=(e=>{const[t]=o.validate(e);return!t}),a.validate=(e=>{const[t,r]=o.validate(e);return t?[new n(t)]:[void 0,r]}),a}return Object.keys(j).forEach(e=>{const n=j[e];r[e]=((e,i,o)=>{return r(n(e,i,f({},o,{types:t})),i,o)})}),r}["arguments","array","boolean","buffer","error","float32array","float64array","function","generatorfunction","int16array","int32array","int8array","map","null","number","object","promise","regexp","set","string","symbol","uint16array","uint32array","uint8array","uint8clampedarray","undefined","weakmap","weakset"].forEach(e=>{$[e]=(t=>o(t)===e)}),$.date=(e=>"date"===o(e)&&!isNaN(e));_()},230:function(e,t,r){"use strict";r.d(t,"a",function(){return n});const n=r(0).f`
  <style>
    ha-switch {
      padding: 16px 0;
    }
    .side-by-side {
      display: flex;
    }
    .side-by-side > * {
      flex: 1;
      padding-right: 4px;
    }
    .suffix {
      margin: 0 8px;
    }
  </style>
`},758:function(e,t,r){"use strict";r.r(t),r.d(t,"HuiIframeCardEditor",function(){return h});var n=r(0),i=(r(81),r(204)),o=r(14),a=r(230);function s(e){var t,r=d(e.key);"method"===e.kind?t={value:e.value,writable:!0,configurable:!0,enumerable:!1}:"get"===e.kind?t={get:e.value,configurable:!0,enumerable:!1}:"set"===e.kind?t={set:e.value,configurable:!0,enumerable:!1}:"field"===e.kind&&(t={configurable:!0,writable:!0,enumerable:!0});var n={kind:"field"===e.kind?"field":"method",key:r,placement:e.static?"static":"field"===e.kind?"own":"prototype",descriptor:t};return e.decorators&&(n.decorators=e.decorators),"field"===e.kind&&(n.initializer=e.value),n}function c(e,t){void 0!==e.descriptor.get?t.descriptor.get=e.descriptor.get:t.descriptor.set=e.descriptor.set}function u(e){return e.decorators&&e.decorators.length}function l(e){return void 0!==e&&!(void 0===e.value&&void 0===e.writable)}function f(e,t){var r=e[t];if(void 0!==r&&"function"!=typeof r)throw new TypeError("Expected '"+t+"' to be a function");return r}function d(e){var t=function(e,t){if("object"!=typeof e||null===e)return e;var r=e[Symbol.toPrimitive];if(void 0!==r){var n=r.call(e,t||"default");if("object"!=typeof n)return n;throw new TypeError("@@toPrimitive must return a primitive value.")}return("string"===t?String:Number)(e)}(e,"string");return"symbol"==typeof t?t:String(t)}const p=Object(i.a)({type:"string",title:"string?",url:"string?",aspect_ratio:"string?"});let h=function(e,t,r,n){var i=function(){var e={elementsDefinitionOrder:[["method"],["field"]],initializeInstanceElements:function(e,t){["method","field"].forEach(function(r){t.forEach(function(t){t.kind===r&&"own"===t.placement&&this.defineClassElement(e,t)},this)},this)},initializeClassElements:function(e,t){var r=e.prototype;["method","field"].forEach(function(n){t.forEach(function(t){var i=t.placement;if(t.kind===n&&("static"===i||"prototype"===i)){var o="static"===i?e:r;this.defineClassElement(o,t)}},this)},this)},defineClassElement:function(e,t){var r=t.descriptor;if("field"===t.kind){var n=t.initializer;r={enumerable:r.enumerable,writable:r.writable,configurable:r.configurable,value:void 0===n?void 0:n.call(e)}}Object.defineProperty(e,t.key,r)},decorateClass:function(e,t){var r=[],n=[],i={static:[],prototype:[],own:[]};if(e.forEach(function(e){this.addElementPlacement(e,i)},this),e.forEach(function(e){if(!u(e))return r.push(e);var t=this.decorateElement(e,i);r.push(t.element),r.push.apply(r,t.extras),n.push.apply(n,t.finishers)},this),!t)return{elements:r,finishers:n};var o=this.decorateConstructor(r,t);return n.push.apply(n,o.finishers),o.finishers=n,o},addElementPlacement:function(e,t,r){var n=t[e.placement];if(!r&&-1!==n.indexOf(e.key))throw new TypeError("Duplicated element ("+e.key+")");n.push(e.key)},decorateElement:function(e,t){for(var r=[],n=[],i=e.decorators,o=i.length-1;o>=0;o--){var a=t[e.placement];a.splice(a.indexOf(e.key),1);var s=this.fromElementDescriptor(e),c=this.toElementFinisherExtras((0,i[o])(s)||s);e=c.element,this.addElementPlacement(e,t),c.finisher&&n.push(c.finisher);var u=c.extras;if(u){for(var l=0;l<u.length;l++)this.addElementPlacement(u[l],t);r.push.apply(r,u)}}return{element:e,finishers:n,extras:r}},decorateConstructor:function(e,t){for(var r=[],n=t.length-1;n>=0;n--){var i=this.fromClassDescriptor(e),o=this.toClassDescriptor((0,t[n])(i)||i);if(void 0!==o.finisher&&r.push(o.finisher),void 0!==o.elements){e=o.elements;for(var a=0;a<e.length-1;a++)for(var s=a+1;s<e.length;s++)if(e[a].key===e[s].key&&e[a].placement===e[s].placement)throw new TypeError("Duplicated element ("+e[a].key+")")}}return{elements:e,finishers:r}},fromElementDescriptor:function(e){var t={kind:e.kind,key:e.key,placement:e.placement,descriptor:e.descriptor};return Object.defineProperty(t,Symbol.toStringTag,{value:"Descriptor",configurable:!0}),"field"===e.kind&&(t.initializer=e.initializer),t},toElementDescriptors:function(e){var t;if(void 0!==e)return(t=e,function(e){if(Array.isArray(e))return e}(t)||function(e){if(Symbol.iterator in Object(e)||"[object Arguments]"===Object.prototype.toString.call(e))return Array.from(e)}(t)||function(){throw new TypeError("Invalid attempt to destructure non-iterable instance")}()).map(function(e){var t=this.toElementDescriptor(e);return this.disallowProperty(e,"finisher","An element descriptor"),this.disallowProperty(e,"extras","An element descriptor"),t},this)},toElementDescriptor:function(e){var t=String(e.kind);if("method"!==t&&"field"!==t)throw new TypeError('An element descriptor\'s .kind property must be either "method" or "field", but a decorator created an element descriptor with .kind "'+t+'"');var r=d(e.key),n=String(e.placement);if("static"!==n&&"prototype"!==n&&"own"!==n)throw new TypeError('An element descriptor\'s .placement property must be one of "static", "prototype" or "own", but a decorator created an element descriptor with .placement "'+n+'"');var i=e.descriptor;this.disallowProperty(e,"elements","An element descriptor");var o={kind:t,key:r,placement:n,descriptor:Object.assign({},i)};return"field"!==t?this.disallowProperty(e,"initializer","A method descriptor"):(this.disallowProperty(i,"get","The property descriptor of a field descriptor"),this.disallowProperty(i,"set","The property descriptor of a field descriptor"),this.disallowProperty(i,"value","The property descriptor of a field descriptor"),o.initializer=e.initializer),o},toElementFinisherExtras:function(e){var t=this.toElementDescriptor(e),r=f(e,"finisher"),n=this.toElementDescriptors(e.extras);return{element:t,finisher:r,extras:n}},fromClassDescriptor:function(e){var t={kind:"class",elements:e.map(this.fromElementDescriptor,this)};return Object.defineProperty(t,Symbol.toStringTag,{value:"Descriptor",configurable:!0}),t},toClassDescriptor:function(e){var t=String(e.kind);if("class"!==t)throw new TypeError('A class descriptor\'s .kind property must be "class", but a decorator created a class descriptor with .kind "'+t+'"');this.disallowProperty(e,"key","A class descriptor"),this.disallowProperty(e,"placement","A class descriptor"),this.disallowProperty(e,"descriptor","A class descriptor"),this.disallowProperty(e,"initializer","A class descriptor"),this.disallowProperty(e,"extras","A class descriptor");var r=f(e,"finisher"),n=this.toElementDescriptors(e.elements);return{elements:n,finisher:r}},runClassFinishers:function(e,t){for(var r=0;r<t.length;r++){var n=(0,t[r])(e);if(void 0!==n){if("function"!=typeof n)throw new TypeError("Finishers must return a constructor.");e=n}}return e},disallowProperty:function(e,t,r){if(void 0!==e[t])throw new TypeError(r+" can't have a ."+t+" property.")}};return e}();if(n)for(var o=0;o<n.length;o++)i=n[o](i);var a=t(function(e){i.initializeInstanceElements(e,p.elements)},r),p=i.decorateClass(function(e){for(var t=[],r=function(e){return"method"===e.kind&&e.key===o.key&&e.placement===o.placement},n=0;n<e.length;n++){var i,o=e[n];if("method"===o.kind&&(i=t.find(r)))if(l(o.descriptor)||l(i.descriptor)){if(u(o)||u(i))throw new ReferenceError("Duplicated methods ("+o.key+") can't be decorated.");i.descriptor=o.descriptor}else{if(u(o)){if(u(i))throw new ReferenceError("Decorators can't be placed on different accessors with for the same property ("+o.key+").");i.decorators=o.decorators}c(o,i)}else t.push(o)}return t}(a.d.map(s)),e);return i.initializeClassElements(a.F,p.elements),i.runClassFinishers(a.F,p.finishers)}([Object(n.d)("hui-iframe-card-editor")],function(e,t){return{F:class extends t{constructor(...t){super(...t),e(this)}},d:[{kind:"field",decorators:[Object(n.g)()],key:"hass",value:void 0},{kind:"field",decorators:[Object(n.g)()],key:"_config",value:void 0},{kind:"method",key:"setConfig",value:function(e){e=p(e),this._config=e}},{kind:"get",key:"_title",value:function(){return this._config.title||""}},{kind:"get",key:"_url",value:function(){return this._config.url||""}},{kind:"get",key:"_aspect_ratio",value:function(){return this._config.aspect_ratio||""}},{kind:"method",key:"render",value:function(){return this.hass?n.f`
      ${a.a}
      <div class="card-config">
        <paper-input
          .label="${this.hass.localize("ui.panel.lovelace.editor.card.generic.url")} (${this.hass.localize("ui.panel.lovelace.editor.card.config.required")})"
          .value="${this._url}"
          .configValue="${"url"}"
          @value-changed="${this._valueChanged}"
        ></paper-input>
        <div class="side-by-side">
          <paper-input
            .label="${this.hass.localize("ui.panel.lovelace.editor.card.generic.title")} (${this.hass.localize("ui.panel.lovelace.editor.card.config.optional")})"
            .value="${this._title}"
            .configValue="${"title"}"
            @value-changed="${this._valueChanged}"
          ></paper-input>
          <paper-input
            .label="${this.hass.localize("ui.panel.lovelace.editor.card.generic.aspect_ratio")} (${this.hass.localize("ui.panel.lovelace.editor.card.config.optional")})"
            type="number"
            .value="${Number(this._aspect_ratio.replace("%",""))}"
            .configValue="${"aspect_ratio"}"
            @value-changed="${this._valueChanged}"
          ></paper-input>
        </div>
      </div>
    `:n.f``}},{kind:"method",key:"_valueChanged",value:function(e){if(!this._config||!this.hass)return;const t=e.target;let r=t.value;"aspect_ratio"===t.configValue&&t.value&&(r+="%"),this[`_${t.configValue}`]!==r&&(t.configValue&&(""===t.value?delete this._config[t.configValue]:this._config=Object.assign({},this._config,{[t.configValue]:r})),Object(o.a)(this,"config-changed",{config:this._config}))}}]}},n.a)}}]);
//# sourceMappingURL=chunk.ffbae986ab21fbcc21a4.js.map
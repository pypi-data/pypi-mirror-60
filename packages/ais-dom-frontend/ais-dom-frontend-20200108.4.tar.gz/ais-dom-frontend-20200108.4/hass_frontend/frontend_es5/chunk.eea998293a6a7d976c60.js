(self.webpackJsonp=self.webpackJsonp||[]).push([[122],{250:function(e,t,r){"use strict";var n=r(70),i=r(0),o=r(72);r(262);function a(e){return(a="function"==typeof Symbol&&"symbol"==typeof Symbol.iterator?function(e){return typeof e}:function(e){return e&&"function"==typeof Symbol&&e.constructor===Symbol&&e!==Symbol.prototype?"symbol":typeof e})(e)}function s(){var e=u(["\n              <ha-icon .icon=","></ha-icon>\n            "]);return s=function(){return e},e}function c(){var e=u(['\n      <button\n        .ripple="','"\n        class="mdc-fab ','"\n        ?disabled="','"\n        aria-label="','"\n      >\n        ',"\n        ","\n        ","\n      </button>\n    "]);return c=function(){return e},e}function u(e,t){return t||(t=e.slice(0)),Object.freeze(Object.defineProperties(e,{raw:{value:Object.freeze(t)}}))}function l(e){return(l=Object.setPrototypeOf?Object.getPrototypeOf:function(e){return e.__proto__||Object.getPrototypeOf(e)})(e)}function f(e){if(void 0===e)throw new ReferenceError("this hasn't been initialised - super() hasn't been called");return e}function p(e,t){return(p=Object.setPrototypeOf||function(e,t){return e.__proto__=t,e})(e,t)}function d(e){var t,r=v(e.key);"method"===e.kind?t={value:e.value,writable:!0,configurable:!0,enumerable:!1}:"get"===e.kind?t={get:e.value,configurable:!0,enumerable:!1}:"set"===e.kind?t={set:e.value,configurable:!0,enumerable:!1}:"field"===e.kind&&(t={configurable:!0,writable:!0,enumerable:!0});var n={kind:"field"===e.kind?"field":"method",key:r,placement:e.static?"static":"field"===e.kind?"own":"prototype",descriptor:t};return e.decorators&&(n.decorators=e.decorators),"field"===e.kind&&(n.initializer=e.value),n}function h(e,t){void 0!==e.descriptor.get?t.descriptor.get=e.descriptor.get:t.descriptor.set=e.descriptor.set}function m(e){return e.decorators&&e.decorators.length}function y(e){return void 0!==e&&!(void 0===e.value&&void 0===e.writable)}function b(e,t){var r=e[t];if(void 0!==r&&"function"!=typeof r)throw new TypeError("Expected '"+t+"' to be a function");return r}function v(e){var t=function(e,t){if("object"!==a(e)||null===e)return e;var r=e[Symbol.toPrimitive];if(void 0!==r){var n=r.call(e,t||"default");if("object"!==a(n))return n;throw new TypeError("@@toPrimitive must return a primitive value.")}return("string"===t?String:Number)(e)}(e,"string");return"symbol"===a(t)?t:String(t)}var g=customElements.get("mwc-fab");!function(e,t,r,n){var i=function(){var e={elementsDefinitionOrder:[["method"],["field"]],initializeInstanceElements:function(e,t){["method","field"].forEach(function(r){t.forEach(function(t){t.kind===r&&"own"===t.placement&&this.defineClassElement(e,t)},this)},this)},initializeClassElements:function(e,t){var r=e.prototype;["method","field"].forEach(function(n){t.forEach(function(t){var i=t.placement;if(t.kind===n&&("static"===i||"prototype"===i)){var o="static"===i?e:r;this.defineClassElement(o,t)}},this)},this)},defineClassElement:function(e,t){var r=t.descriptor;if("field"===t.kind){var n=t.initializer;r={enumerable:r.enumerable,writable:r.writable,configurable:r.configurable,value:void 0===n?void 0:n.call(e)}}Object.defineProperty(e,t.key,r)},decorateClass:function(e,t){var r=[],n=[],i={static:[],prototype:[],own:[]};if(e.forEach(function(e){this.addElementPlacement(e,i)},this),e.forEach(function(e){if(!m(e))return r.push(e);var t=this.decorateElement(e,i);r.push(t.element),r.push.apply(r,t.extras),n.push.apply(n,t.finishers)},this),!t)return{elements:r,finishers:n};var o=this.decorateConstructor(r,t);return n.push.apply(n,o.finishers),o.finishers=n,o},addElementPlacement:function(e,t,r){var n=t[e.placement];if(!r&&-1!==n.indexOf(e.key))throw new TypeError("Duplicated element ("+e.key+")");n.push(e.key)},decorateElement:function(e,t){for(var r=[],n=[],i=e.decorators,o=i.length-1;o>=0;o--){var a=t[e.placement];a.splice(a.indexOf(e.key),1);var s=this.fromElementDescriptor(e),c=this.toElementFinisherExtras((0,i[o])(s)||s);e=c.element,this.addElementPlacement(e,t),c.finisher&&n.push(c.finisher);var u=c.extras;if(u){for(var l=0;l<u.length;l++)this.addElementPlacement(u[l],t);r.push.apply(r,u)}}return{element:e,finishers:n,extras:r}},decorateConstructor:function(e,t){for(var r=[],n=t.length-1;n>=0;n--){var i=this.fromClassDescriptor(e),o=this.toClassDescriptor((0,t[n])(i)||i);if(void 0!==o.finisher&&r.push(o.finisher),void 0!==o.elements){e=o.elements;for(var a=0;a<e.length-1;a++)for(var s=a+1;s<e.length;s++)if(e[a].key===e[s].key&&e[a].placement===e[s].placement)throw new TypeError("Duplicated element ("+e[a].key+")")}}return{elements:e,finishers:r}},fromElementDescriptor:function(e){var t={kind:e.kind,key:e.key,placement:e.placement,descriptor:e.descriptor};return Object.defineProperty(t,Symbol.toStringTag,{value:"Descriptor",configurable:!0}),"field"===e.kind&&(t.initializer=e.initializer),t},toElementDescriptors:function(e){var t;if(void 0!==e)return(t=e,function(e){if(Array.isArray(e))return e}(t)||function(e){if(Symbol.iterator in Object(e)||"[object Arguments]"===Object.prototype.toString.call(e))return Array.from(e)}(t)||function(){throw new TypeError("Invalid attempt to destructure non-iterable instance")}()).map(function(e){var t=this.toElementDescriptor(e);return this.disallowProperty(e,"finisher","An element descriptor"),this.disallowProperty(e,"extras","An element descriptor"),t},this)},toElementDescriptor:function(e){var t=String(e.kind);if("method"!==t&&"field"!==t)throw new TypeError('An element descriptor\'s .kind property must be either "method" or "field", but a decorator created an element descriptor with .kind "'+t+'"');var r=v(e.key),n=String(e.placement);if("static"!==n&&"prototype"!==n&&"own"!==n)throw new TypeError('An element descriptor\'s .placement property must be one of "static", "prototype" or "own", but a decorator created an element descriptor with .placement "'+n+'"');var i=e.descriptor;this.disallowProperty(e,"elements","An element descriptor");var o={kind:t,key:r,placement:n,descriptor:Object.assign({},i)};return"field"!==t?this.disallowProperty(e,"initializer","A method descriptor"):(this.disallowProperty(i,"get","The property descriptor of a field descriptor"),this.disallowProperty(i,"set","The property descriptor of a field descriptor"),this.disallowProperty(i,"value","The property descriptor of a field descriptor"),o.initializer=e.initializer),o},toElementFinisherExtras:function(e){var t=this.toElementDescriptor(e),r=b(e,"finisher"),n=this.toElementDescriptors(e.extras);return{element:t,finisher:r,extras:n}},fromClassDescriptor:function(e){var t={kind:"class",elements:e.map(this.fromElementDescriptor,this)};return Object.defineProperty(t,Symbol.toStringTag,{value:"Descriptor",configurable:!0}),t},toClassDescriptor:function(e){var t=String(e.kind);if("class"!==t)throw new TypeError('A class descriptor\'s .kind property must be "class", but a decorator created a class descriptor with .kind "'+t+'"');this.disallowProperty(e,"key","A class descriptor"),this.disallowProperty(e,"placement","A class descriptor"),this.disallowProperty(e,"descriptor","A class descriptor"),this.disallowProperty(e,"initializer","A class descriptor"),this.disallowProperty(e,"extras","A class descriptor");var r=b(e,"finisher"),n=this.toElementDescriptors(e.elements);return{elements:n,finisher:r}},runClassFinishers:function(e,t){for(var r=0;r<t.length;r++){var n=(0,t[r])(e);if(void 0!==n){if("function"!=typeof n)throw new TypeError("Finishers must return a constructor.");e=n}}return e},disallowProperty:function(e,t,r){if(void 0!==e[t])throw new TypeError(r+" can't have a ."+t+" property.")}};return e}();if(n)for(var o=0;o<n.length;o++)i=n[o](i);var a=t(function(e){i.initializeInstanceElements(e,s.elements)},r),s=i.decorateClass(function(e){for(var t=[],r=function(e){return"method"===e.kind&&e.key===o.key&&e.placement===o.placement},n=0;n<e.length;n++){var i,o=e[n];if("method"===o.kind&&(i=t.find(r)))if(y(o.descriptor)||y(i.descriptor)){if(m(o)||m(i))throw new ReferenceError("Duplicated methods ("+o.key+") can't be decorated.");i.descriptor=o.descriptor}else{if(m(o)){if(m(i))throw new ReferenceError("Decorators can't be placed on different accessors with for the same property ("+o.key+").");i.decorators=o.decorators}h(o,i)}else t.push(o)}return t}(a.d.map(d)),e);i.initializeClassElements(a.F,s.elements),i.runClassFinishers(a.F,s.finishers)}([Object(i.d)("ha-fab")],function(e,t){return{F:function(r){function n(){var t,r,i,o;!function(e,t){if(!(e instanceof t))throw new TypeError("Cannot call a class as a function")}(this,n);for(var s=arguments.length,c=new Array(s),u=0;u<s;u++)c[u]=arguments[u];return i=this,r=!(o=(t=l(n)).call.apply(t,[this].concat(c)))||"object"!==a(o)&&"function"!=typeof o?f(i):o,e(f(r)),r}return function(e,t){if("function"!=typeof t&&null!==t)throw new TypeError("Super expression must either be null or a function");e.prototype=Object.create(t&&t.prototype,{constructor:{value:e,writable:!0,configurable:!0}}),t&&p(e,t)}(n,t),n}(),d:[{kind:"method",key:"render",value:function(){var e={"mdc-fab--mini":this.mini,"mdc-fab--exited":this.exited,"mdc-fab--extended":this.extended},t=""!==this.label&&this.extended;return Object(i.f)(c(),Object(o.a)(),Object(n.a)(e),this.disabled,this.label||this.icon,t&&this.showIconAtEnd?this.label:"",this.icon?Object(i.f)(s(),this.icon):"",t&&!this.showIconAtEnd?this.label:"")}}]}},g)},275:function(e,t,r){"use strict";r(108);var n=r(180);function i(e){return(i="function"==typeof Symbol&&"symbol"==typeof Symbol.iterator?function(e){return typeof e}:function(e){return e&&"function"==typeof Symbol&&e.constructor===Symbol&&e!==Symbol.prototype?"symbol":typeof e})(e)}function o(e,t){for(var r=0;r<t.length;r++){var n=t[r];n.enumerable=n.enumerable||!1,n.configurable=!0,"value"in n&&(n.writable=!0),Object.defineProperty(e,n.key,n)}}function a(e,t){return!t||"object"!==i(t)&&"function"!=typeof t?function(e){if(void 0===e)throw new ReferenceError("this hasn't been initialised - super() hasn't been called");return e}(e):t}function s(e,t,r){return(s="undefined"!=typeof Reflect&&Reflect.get?Reflect.get:function(e,t,r){var n=function(e,t){for(;!Object.prototype.hasOwnProperty.call(e,t)&&null!==(e=c(e)););return e}(e,t);if(n){var i=Object.getOwnPropertyDescriptor(n,t);return i.get?i.get.call(r):i.value}})(e,t,r||e)}function c(e){return(c=Object.setPrototypeOf?Object.getPrototypeOf:function(e){return e.__proto__||Object.getPrototypeOf(e)})(e)}function u(e,t){return(u=Object.setPrototypeOf||function(e,t){return e.__proto__=t,e})(e,t)}var l=function(e){function t(){return function(e,t){if(!(e instanceof t))throw new TypeError("Cannot call a class as a function")}(this,t),a(this,c(t).apply(this,arguments))}var r,i,l;return function(e,t){if("function"!=typeof t&&null!==t)throw new TypeError("Super expression must either be null or a function");e.prototype=Object.create(t&&t.prototype,{constructor:{value:e,writable:!0,configurable:!0}}),t&&u(e,t)}(t,n["a"]),r=t,(i=[{key:"connectedCallback",value:function(){var e=this;s(c(t.prototype),"connectedCallback",this).call(this),setTimeout(function(){e.icon="ltr"===window.getComputedStyle(e).direction?"hass:chevron-right":"hass:chevron-left"},100)}}])&&o(r.prototype,i),l&&o(r,l),t}();customElements.define("ha-icon-next",l)},347:function(e,t,r){"use strict";r.d(t,"a",function(){return i});var n=r(46),i=function(e,t){return Object(n.a)(e,{message:t.localize("ui.common.successfully_saved")})}},388:function(e,t,r){"use strict";r.d(t,"a",function(){return n}),r.d(t,"b",function(){return i}),r.d(t,"d",function(){return o}),r.d(t,"e",function(){return a}),r.d(t,"c",function(){return s});var n="system-admin",i="system-users",o=function(e){return regeneratorRuntime.async(function(t){for(;;)switch(t.prev=t.next){case 0:return t.abrupt("return",e.callWS({type:"config/auth/list"}));case 1:case"end":return t.stop()}})},a=function(e,t,r){return regeneratorRuntime.async(function(n){for(;;)switch(n.prev=n.next){case 0:return n.abrupt("return",e.callWS(Object.assign({},r,{type:"config/auth/update",user_id:t})));case 1:case"end":return n.stop()}})},s=function(e,t){return regeneratorRuntime.async(function(r){for(;;)switch(r.prev=r.next){case 0:return r.abrupt("return",e.callWS({type:"config/auth/delete",user_id:t}));case 1:case"end":return r.stop()}})}},816:function(e,t,r){"use strict";r.r(t);r(234);var n=r(11),i=r(21),o=r(4),a=r(29),s=r(306),c=(r(142),r(185),r(149),r(275),r(178),r(250),r(176)),u=r(183),l=r(94);function f(e){return(f="function"==typeof Symbol&&"symbol"==typeof Symbol.iterator?function(e){return typeof e}:function(e){return e&&"function"==typeof Symbol&&e.constructor===Symbol&&e!==Symbol.prototype?"symbol":typeof e})(e)}function p(){var e=function(e,t){t||(t=e.slice(0));return Object.freeze(Object.defineProperties(e,{raw:{value:Object.freeze(t)}}))}(['\n      <style>\n        ha-fab {\n          position: fixed;\n          bottom: 16px;\n          right: 16px;\n          z-index: 1;\n        }\n        ha-fab[is-wide] {\n          bottom: 24px;\n          right: 24px;\n        }\n        ha-fab[rtl] {\n          right: auto;\n          left: 16px;\n        }\n        ha-fab[rtl][is-wide] {\n          bottom: 24px;\n          right: auto;\n          left: 24px;\n        }\n\n        ha-card {\n          max-width: 600px;\n          margin: 16px auto;\n          overflow: hidden;\n        }\n        a {\n          text-decoration: none;\n          color: var(--primary-text-color);\n        }\n      </style>\n\n      <hass-subpage header="[[localize(\'ui.panel.config.users.picker.title\')]]">\n        <ha-card>\n          <template is="dom-repeat" items="[[users]]" as="user">\n            <a href="[[_computeUrl(user)]]">\n              <paper-item>\n                <paper-item-body two-line>\n                  <div>[[_withDefault(user.name, \'Unnamed User\')]]</div>\n                  <div secondary="">\n                    [[_computeGroup(localize, user)]]\n                    <template is="dom-if" if="[[user.system_generated]]">\n                      -\n                      [[localize(\'ui.panel.config.users.picker.system_generated\')]]\n                    </template>\n                  </div>\n                </paper-item-body>\n                <ha-icon-next></ha-icon-next>\n              </paper-item>\n            </a>\n          </template>\n        </ha-card>\n\n        <ha-fab\n          is-wide$="[[isWide]]"\n          icon="hass:plus"\n          title="[[localize(\'ui.panel.config.users.picker.add_user\')]]"\n          on-click="_addUser"\n          rtl$="[[rtl]]"\n        ></ha-fab>\n      </hass-subpage>\n    ']);return p=function(){return e},e}function d(e,t){for(var r=0;r<t.length;r++){var n=t[r];n.enumerable=n.enumerable||!1,n.configurable=!0,"value"in n&&(n.writable=!0),Object.defineProperty(e,n.key,n)}}function h(e,t){return!t||"object"!==f(t)&&"function"!=typeof t?function(e){if(void 0===e)throw new ReferenceError("this hasn't been initialised - super() hasn't been called");return e}(e):t}function m(e,t,r){return(m="undefined"!=typeof Reflect&&Reflect.get?Reflect.get:function(e,t,r){var n=function(e,t){for(;!Object.prototype.hasOwnProperty.call(e,t)&&null!==(e=y(e)););return e}(e,t);if(n){var i=Object.getOwnPropertyDescriptor(n,t);return i.get?i.get.call(r):i.value}})(e,t,r||e)}function y(e){return(y=Object.setPrototypeOf?Object.getPrototypeOf:function(e){return e.__proto__||Object.getPrototypeOf(e)})(e)}function b(e,t){return(b=Object.setPrototypeOf||function(e,t){return e.__proto__=t,e})(e,t)}var v=!1,g=function(e){function t(){return function(e,t){if(!(e instanceof t))throw new TypeError("Cannot call a class as a function")}(this,t),h(this,y(t).apply(this,arguments))}var n,i,f;return function(e,t){if("function"!=typeof t&&null!==t)throw new TypeError("Super expression must either be null or a function");e.prototype=Object.create(t&&t.prototype,{constructor:{value:e,writable:!0,configurable:!0}}),t&&b(e,t)}(t,Object(u["a"])(Object(s["a"])(Object(c["a"])(a["a"])))),n=t,f=[{key:"template",get:function(){return Object(o.a)(p())}},{key:"properties",get:function(){return{hass:Object,users:Array,rtl:{type:Boolean,reflectToAttribute:!0,computed:"_computeRTL(hass)"}}}}],(i=[{key:"connectedCallback",value:function(){m(y(t.prototype),"connectedCallback",this).call(this),v||(v=!0,this.fire("register-dialog",{dialogShowEvent:"show-add-user",dialogTag:"ha-dialog-add-user",dialogImport:function(){return Promise.all([r.e(1),r.e(47)]).then(r.bind(null,788))}}))}},{key:"_withDefault",value:function(e,t){return e||t}},{key:"_computeUrl",value:function(e){return"/config/users/".concat(e.id)}},{key:"_computeGroup",value:function(e,t){return e("groups.".concat(t.group_ids[0]))}},{key:"_computeRTL",value:function(e){return Object(l.a)(e)}},{key:"_addUser",value:function(){var e=this;this.fire("show-add-user",{hass:this.hass,dialogClosedCallback:function(t){var r;return regeneratorRuntime.async(function(n){for(;;)switch(n.prev=n.next){case 0:r=t.userId,e.fire("reload-users"),r&&e.navigate("/config/users/".concat(r));case 3:case"end":return n.stop()}})}})}}])&&d(n.prototype,i),f&&d(n,f),t}();customElements.define("ha-config-user-picker",g);var w=r(0),k=r(711),O=(r(84),r(54)),_=r(14),E=r(97),j=r(388),P=r(347);function x(e){return(x="function"==typeof Symbol&&"symbol"==typeof Symbol.iterator?function(e){return typeof e}:function(e){return e&&"function"==typeof Symbol&&e.constructor===Symbol&&e!==Symbol.prototype?"symbol":typeof e})(e)}function S(){var e=R(["\n        .card-actions {\n          display: flex;\n          justify-content: space-between;\n          align-items: center;\n        }\n        ha-card {\n          max-width: 600px;\n          margin: 0 auto 16px;\n        }\n        hass-subpage ha-card:first-of-type {\n          direction: ltr;\n        }\n        table {\n          width: 100%;\n        }\n        td {\n          vertical-align: top;\n        }\n        .user-experiment {\n          padding: 8px 0;\n        }\n      "]);return S=function(){return e},e}function z(){var e=R(["\n                  ","\n                "]);return z=function(){return e},e}function D(){var e=R(['\n                  <tr>\n                    <td colspan="2" class="user-experiment">\n                      The users group is a work in progress. The user will be\n                      unable to administer the instance via the UI. We\'re still\n                      auditing all management API endpoints to ensure that they\n                      correctly limit access to administrators.\n                    </td>\n                  </tr>\n                ']);return D=function(){return e},e}function T(){var e=R(["\n                      <option value=",">\n                        ","\n                      </option>\n                    "]);return T=function(){return e},e}function C(){var e=R(["\n      <hass-subpage\n        .header=","\n      >\n        <ha-card .header=",'>\n          <table class="card-content">\n            <tr>\n              <td>',"</td>\n              <td>","</td>\n            </tr>\n            <tr>\n              <td>","</td>\n              <td>","</td>\n            </tr>\n            <tr>\n              <td>","</td>\n              <td>\n                <select\n                  @change=","\n                  .value=","\n                >\n                  ","\n                </select>\n              </td>\n            </tr>\n            ","\n\n            <tr>\n              <td>","</td>\n              <td>","</td>\n            </tr>\n            <tr>\n              <td>\n                ","\n              </td>\n              <td>",'</td>\n            </tr>\n          </table>\n\n          <div class="card-actions">\n            <mwc-button @click=',">\n              ",'\n            </mwc-button>\n            <mwc-button\n              class="warning"\n              @click=',"\n              .disabled=","\n            >\n              ","\n            </mwc-button>\n            ","\n          </div>\n        </ha-card>\n      </hass-subpage>\n    "]);return C=function(){return e},e}function A(){var e=R([""]);return A=function(){return e},e}function R(e,t){return t||(t=e.slice(0)),Object.freeze(Object.defineProperties(e,{raw:{value:Object.freeze(t)}}))}function F(e){return(F=Object.setPrototypeOf?Object.getPrototypeOf:function(e){return e.__proto__||Object.getPrototypeOf(e)})(e)}function U(e){if(void 0===e)throw new ReferenceError("this hasn't been initialised - super() hasn't been called");return e}function I(e,t){return(I=Object.setPrototypeOf||function(e,t){return e.__proto__=t,e})(e,t)}function W(e){var t,r=N(e.key);"method"===e.kind?t={value:e.value,writable:!0,configurable:!0,enumerable:!1}:"get"===e.kind?t={get:e.value,configurable:!0,enumerable:!1}:"set"===e.kind?t={set:e.value,configurable:!0,enumerable:!1}:"field"===e.kind&&(t={configurable:!0,writable:!0,enumerable:!0});var n={kind:"field"===e.kind?"field":"method",key:r,placement:e.static?"static":"field"===e.kind?"own":"prototype",descriptor:t};return e.decorators&&(n.decorators=e.decorators),"field"===e.kind&&(n.initializer=e.value),n}function G(e,t){void 0!==e.descriptor.get?t.descriptor.get=e.descriptor.get:t.descriptor.set=e.descriptor.set}function q(e){return e.decorators&&e.decorators.length}function L(e){return void 0!==e&&!(void 0===e.value&&void 0===e.writable)}function J(e,t){var r=e[t];if(void 0!==r&&"function"!=typeof r)throw new TypeError("Expected '"+t+"' to be a function");return r}function N(e){var t=function(e,t){if("object"!==x(e)||null===e)return e;var r=e[Symbol.toPrimitive];if(void 0!==r){var n=r.call(e,t||"default");if("object"!==x(n))return n;throw new TypeError("@@toPrimitive must return a primitive value.")}return("string"===t?String:Number)(e)}(e,"string");return"symbol"===x(t)?t:String(t)}var $=[j.b,j.a];!function(e,t,r,n){var i=function(){var e={elementsDefinitionOrder:[["method"],["field"]],initializeInstanceElements:function(e,t){["method","field"].forEach(function(r){t.forEach(function(t){t.kind===r&&"own"===t.placement&&this.defineClassElement(e,t)},this)},this)},initializeClassElements:function(e,t){var r=e.prototype;["method","field"].forEach(function(n){t.forEach(function(t){var i=t.placement;if(t.kind===n&&("static"===i||"prototype"===i)){var o="static"===i?e:r;this.defineClassElement(o,t)}},this)},this)},defineClassElement:function(e,t){var r=t.descriptor;if("field"===t.kind){var n=t.initializer;r={enumerable:r.enumerable,writable:r.writable,configurable:r.configurable,value:void 0===n?void 0:n.call(e)}}Object.defineProperty(e,t.key,r)},decorateClass:function(e,t){var r=[],n=[],i={static:[],prototype:[],own:[]};if(e.forEach(function(e){this.addElementPlacement(e,i)},this),e.forEach(function(e){if(!q(e))return r.push(e);var t=this.decorateElement(e,i);r.push(t.element),r.push.apply(r,t.extras),n.push.apply(n,t.finishers)},this),!t)return{elements:r,finishers:n};var o=this.decorateConstructor(r,t);return n.push.apply(n,o.finishers),o.finishers=n,o},addElementPlacement:function(e,t,r){var n=t[e.placement];if(!r&&-1!==n.indexOf(e.key))throw new TypeError("Duplicated element ("+e.key+")");n.push(e.key)},decorateElement:function(e,t){for(var r=[],n=[],i=e.decorators,o=i.length-1;o>=0;o--){var a=t[e.placement];a.splice(a.indexOf(e.key),1);var s=this.fromElementDescriptor(e),c=this.toElementFinisherExtras((0,i[o])(s)||s);e=c.element,this.addElementPlacement(e,t),c.finisher&&n.push(c.finisher);var u=c.extras;if(u){for(var l=0;l<u.length;l++)this.addElementPlacement(u[l],t);r.push.apply(r,u)}}return{element:e,finishers:n,extras:r}},decorateConstructor:function(e,t){for(var r=[],n=t.length-1;n>=0;n--){var i=this.fromClassDescriptor(e),o=this.toClassDescriptor((0,t[n])(i)||i);if(void 0!==o.finisher&&r.push(o.finisher),void 0!==o.elements){e=o.elements;for(var a=0;a<e.length-1;a++)for(var s=a+1;s<e.length;s++)if(e[a].key===e[s].key&&e[a].placement===e[s].placement)throw new TypeError("Duplicated element ("+e[a].key+")")}}return{elements:e,finishers:r}},fromElementDescriptor:function(e){var t={kind:e.kind,key:e.key,placement:e.placement,descriptor:e.descriptor};return Object.defineProperty(t,Symbol.toStringTag,{value:"Descriptor",configurable:!0}),"field"===e.kind&&(t.initializer=e.initializer),t},toElementDescriptors:function(e){var t;if(void 0!==e)return(t=e,function(e){if(Array.isArray(e))return e}(t)||function(e){if(Symbol.iterator in Object(e)||"[object Arguments]"===Object.prototype.toString.call(e))return Array.from(e)}(t)||function(){throw new TypeError("Invalid attempt to destructure non-iterable instance")}()).map(function(e){var t=this.toElementDescriptor(e);return this.disallowProperty(e,"finisher","An element descriptor"),this.disallowProperty(e,"extras","An element descriptor"),t},this)},toElementDescriptor:function(e){var t=String(e.kind);if("method"!==t&&"field"!==t)throw new TypeError('An element descriptor\'s .kind property must be either "method" or "field", but a decorator created an element descriptor with .kind "'+t+'"');var r=N(e.key),n=String(e.placement);if("static"!==n&&"prototype"!==n&&"own"!==n)throw new TypeError('An element descriptor\'s .placement property must be one of "static", "prototype" or "own", but a decorator created an element descriptor with .placement "'+n+'"');var i=e.descriptor;this.disallowProperty(e,"elements","An element descriptor");var o={kind:t,key:r,placement:n,descriptor:Object.assign({},i)};return"field"!==t?this.disallowProperty(e,"initializer","A method descriptor"):(this.disallowProperty(i,"get","The property descriptor of a field descriptor"),this.disallowProperty(i,"set","The property descriptor of a field descriptor"),this.disallowProperty(i,"value","The property descriptor of a field descriptor"),o.initializer=e.initializer),o},toElementFinisherExtras:function(e){var t=this.toElementDescriptor(e),r=J(e,"finisher"),n=this.toElementDescriptors(e.extras);return{element:t,finisher:r,extras:n}},fromClassDescriptor:function(e){var t={kind:"class",elements:e.map(this.fromElementDescriptor,this)};return Object.defineProperty(t,Symbol.toStringTag,{value:"Descriptor",configurable:!0}),t},toClassDescriptor:function(e){var t=String(e.kind);if("class"!==t)throw new TypeError('A class descriptor\'s .kind property must be "class", but a decorator created a class descriptor with .kind "'+t+'"');this.disallowProperty(e,"key","A class descriptor"),this.disallowProperty(e,"placement","A class descriptor"),this.disallowProperty(e,"descriptor","A class descriptor"),this.disallowProperty(e,"initializer","A class descriptor"),this.disallowProperty(e,"extras","A class descriptor");var r=J(e,"finisher"),n=this.toElementDescriptors(e.elements);return{elements:n,finisher:r}},runClassFinishers:function(e,t){for(var r=0;r<t.length;r++){var n=(0,t[r])(e);if(void 0!==n){if("function"!=typeof n)throw new TypeError("Finishers must return a constructor.");e=n}}return e},disallowProperty:function(e,t,r){if(void 0!==e[t])throw new TypeError(r+" can't have a ."+t+" property.")}};return e}();if(n)for(var o=0;o<n.length;o++)i=n[o](i);var a=t(function(e){i.initializeInstanceElements(e,s.elements)},r),s=i.decorateClass(function(e){for(var t=[],r=function(e){return"method"===e.kind&&e.key===o.key&&e.placement===o.placement},n=0;n<e.length;n++){var i,o=e[n];if("method"===o.kind&&(i=t.find(r)))if(L(o.descriptor)||L(i.descriptor)){if(q(o)||q(i))throw new ReferenceError("Duplicated methods ("+o.key+") can't be decorated.");i.descriptor=o.descriptor}else{if(q(o)){if(q(i))throw new ReferenceError("Decorators can't be placed on different accessors with for the same property ("+o.key+").");i.decorators=o.decorators}G(o,i)}else t.push(o)}return t}(a.d.map(W)),e);i.initializeClassElements(a.F,s.elements),i.runClassFinishers(a.F,s.finishers)}([Object(w.d)("ha-user-editor")],function(e,t){return{F:function(r){function n(){var t,r,i,o;!function(e,t){if(!(e instanceof t))throw new TypeError("Cannot call a class as a function")}(this,n);for(var a=arguments.length,s=new Array(a),c=0;c<a;c++)s[c]=arguments[c];return i=this,r=!(o=(t=F(n)).call.apply(t,[this].concat(s)))||"object"!==x(o)&&"function"!=typeof o?U(i):o,e(U(r)),r}return function(e,t){if("function"!=typeof t&&null!==t)throw new TypeError("Super expression must either be null or a function");e.prototype=Object.create(t&&t.prototype,{constructor:{value:e,writable:!0,configurable:!0}}),t&&I(e,t)}(n,t),n}(),d:[{kind:"field",decorators:[Object(w.g)()],key:"hass",value:void 0},{kind:"field",decorators:[Object(w.g)()],key:"user",value:void 0},{kind:"method",key:"render",value:function(){var e=this.hass,t=this.user;return e&&t?Object(w.f)(C(),e.localize("ui.panel.config.users.editor.caption"),this._name,e.localize("ui.panel.config.users.editor.id"),t.id,e.localize("ui.panel.config.users.editor.owner"),t.is_owner,e.localize("ui.panel.config.users.editor.group"),this._handleGroupChange,Object(k.a)(this.updateComplete.then(function(){return t.group_ids[0]})),$.map(function(t){return Object(w.f)(T(),t,e.localize("groups.".concat(t)))}),t.group_ids[0]===j.b?Object(w.f)(D()):"",e.localize("ui.panel.config.users.editor.active"),t.is_active,e.localize("ui.panel.config.users.editor.system_generated"),t.system_generated,this._handleRenameUser,e.localize("ui.panel.config.users.editor.rename_user"),this._deleteUser,t.system_generated,e.localize("ui.panel.config.users.editor.delete_user"),t.system_generated?Object(w.f)(z(),e.localize("ui.panel.config.users.editor.system_generated_users_not_removable")):""):Object(w.f)(A())}},{kind:"get",key:"_name",value:function(){return this.user&&(this.user.name||this.hass.localize("ui.panel.config.users.editor.unnamed_user"))}},{kind:"method",key:"_handleRenameUser",value:function(e){var t;return regeneratorRuntime.async(function(r){for(;;)switch(r.prev=r.next){case 0:if(e.currentTarget.blur(),null!==(t=prompt(this.hass.localize("ui.panel.config.users.editor.enter_new_name"),this.user.name))&&t!==this.user.name){r.next=4;break}return r.abrupt("return");case 4:return r.prev=4,r.next=7,regeneratorRuntime.awrap(Object(j.e)(this.hass,this.user.id,{name:t}));case 7:Object(_.a)(this,"reload-users"),r.next=13;break;case 10:r.prev=10,r.t0=r.catch(4),alert("".concat(this.hass.localize("ui.panel.config.users.editor.user_rename_failed")," ").concat(r.t0.message));case 13:case"end":return r.stop()}},null,this,[[4,10]])}},{kind:"method",key:"_handleGroupChange",value:function(e){var t,r;return regeneratorRuntime.async(function(n){for(;;)switch(n.prev=n.next){case 0:return t=e.currentTarget,r=t.value,n.prev=2,n.next=5,regeneratorRuntime.awrap(Object(j.e)(this.hass,this.user.id,{group_ids:[r]}));case 5:Object(P.a)(this,this.hass),Object(_.a)(this,"reload-users"),n.next=13;break;case 9:n.prev=9,n.t0=n.catch(2),alert("".concat(this.hass.localize("ui.panel.config.users.editor.group_update_failed")," ").concat(n.t0.message)),t.value=this.user.group_ids[0];case 13:case"end":return n.stop()}},null,this,[[2,9]])}},{kind:"method",key:"_deleteUser",value:function(e){return regeneratorRuntime.async(function(t){for(;;)switch(t.prev=t.next){case 0:if(confirm(this.hass.localize("ui.panel.config.users.editor.confirm_user_deletion","name",this._name))){t.next=3;break}return e.target.blur(),t.abrupt("return");case 3:return t.prev=3,t.next=6,regeneratorRuntime.awrap(Object(j.c)(this.hass,this.user.id));case 6:t.next=12;break;case 8:return t.prev=8,t.t0=t.catch(3),alert(t.t0.code),t.abrupt("return");case 12:Object(_.a)(this,"reload-users"),Object(E.a)(this,"/config/users");case 14:case"end":return t.stop()}},null,this,[[3,8]])}},{kind:"get",static:!0,key:"styles",value:function(){return[O.a,Object(w.c)(S())]}}]}},w.a);function B(e){return(B="function"==typeof Symbol&&"symbol"==typeof Symbol.iterator?function(e){return typeof e}:function(e){return e&&"function"==typeof Symbol&&e.constructor===Symbol&&e!==Symbol.prototype?"symbol":typeof e})(e)}function H(){var e=function(e,t){t||(t=e.slice(0));return Object.freeze(Object.defineProperties(e,{raw:{value:Object.freeze(t)}}))}(['\n      <app-route\n        route="[[route]]"\n        pattern="/:user"\n        data="{{_routeData}}"\n      ></app-route>\n\n      <template is="dom-if" if=\'[[_equals(_routeData.user, "picker")]]\'>\n        <ha-config-user-picker\n          hass="[[hass]]"\n          users="[[_users]]"\n        ></ha-config-user-picker>\n      </template>\n      <template\n        is="dom-if"\n        if=\'[[!_equals(_routeData.user, "picker")]]\'\n        restamp\n      >\n        <ha-user-editor\n          hass="[[hass]]"\n          user="[[_computeUser(_users, _routeData.user)]]"\n        ></ha-user-editor>\n      </template>\n    ']);return H=function(){return e},e}function K(e,t){for(var r=0;r<t.length;r++){var n=t[r];n.enumerable=n.enumerable||!1,n.configurable=!0,"value"in n&&(n.writable=!0),Object.defineProperty(e,n.key,n)}}function M(e,t){return!t||"object"!==B(t)&&"function"!=typeof t?function(e){if(void 0===e)throw new ReferenceError("this hasn't been initialised - super() hasn't been called");return e}(e):t}function Q(e,t,r){return(Q="undefined"!=typeof Reflect&&Reflect.get?Reflect.get:function(e,t,r){var n=function(e,t){for(;!Object.prototype.hasOwnProperty.call(e,t)&&null!==(e=V(e)););return e}(e,t);if(n){var i=Object.getOwnPropertyDescriptor(n,t);return i.get?i.get.call(r):i.value}})(e,t,r||e)}function V(e){return(V=Object.setPrototypeOf?Object.getPrototypeOf:function(e){return e.__proto__||Object.getPrototypeOf(e)})(e)}function X(e,t){return(X=Object.setPrototypeOf||function(e,t){return e.__proto__=t,e})(e,t)}var Y=function(e){function t(){return function(e,t){if(!(e instanceof t))throw new TypeError("Cannot call a class as a function")}(this,t),M(this,V(t).apply(this,arguments))}var r,c,u;return function(e,t){if("function"!=typeof t&&null!==t)throw new TypeError("Super expression must either be null or a function");e.prototype=Object.create(t&&t.prototype,{constructor:{value:e,writable:!0,configurable:!0}}),t&&X(e,t)}(t,Object(s["a"])(a["a"])),r=t,u=[{key:"template",get:function(){return Object(o.a)(H())}},{key:"properties",get:function(){return{hass:Object,route:{type:Object,observer:"_checkRoute"},_routeData:Object,_user:{type:Object,value:null},_users:{type:Array,value:null}}}}],(c=[{key:"ready",value:function(){var e=this;Q(V(t.prototype),"ready",this).call(this),this._loadData(),this.addEventListener("reload-users",function(){return e._loadData()})}},{key:"_handlePickUser",value:function(e){this._user=e.detail.user}},{key:"_checkRoute",value:function(e){var t=this;Object(_.a)(this,"iron-resize"),this._debouncer=i.a.debounce(this._debouncer,n.d.after(0),function(){""===e.path&&t.navigate("".concat(e.prefix,"/picker"),!0)})}},{key:"_computeUser",value:function(e,t){return e&&e.filter(function(e){return e.id===t})[0]}},{key:"_equals",value:function(e,t){return e===t}},{key:"_loadData",value:function(){return regeneratorRuntime.async(function(e){for(;;)switch(e.prev=e.next){case 0:return e.next=2,regeneratorRuntime.awrap(Object(j.d)(this.hass));case 2:this._users=e.sent;case 3:case"end":return e.stop()}},null,this)}}])&&K(r.prototype,c),u&&K(r,u),t}();customElements.define("ha-config-users",Y)}}]);
//# sourceMappingURL=chunk.eea998293a6a7d976c60.js.map
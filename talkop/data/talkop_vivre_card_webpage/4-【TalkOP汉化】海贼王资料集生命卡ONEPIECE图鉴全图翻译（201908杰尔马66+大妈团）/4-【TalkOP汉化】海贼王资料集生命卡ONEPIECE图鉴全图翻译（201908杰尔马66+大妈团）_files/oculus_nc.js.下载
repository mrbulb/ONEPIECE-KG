
!function (name, definition) {
  if (typeof module != 'undefined') module.exports = definition()
  else if (typeof define == 'function' && typeof define.amd == 'object') define(definition)
  else this[name] = definition()
}('paxmac_ready', function (ready) {
  var fns = [], fn, f = false
    , doc = document
    , testEl = doc.documentElement
    , hack = testEl.doScroll
    , domContentLoaded = 'DOMContentLoaded'
    , addEventListener = 'addEventListener'
    , onreadystatechange = 'onreadystatechange'
    , readyState = 'readyState'
    , loadedRgx = hack ? /^loaded|^c/ : /^loaded|c/
    , loaded = loadedRgx.test(doc[readyState])

  function flush(f) {
    loaded = 1
    while (f = fns.shift()) f()
  }

  doc[addEventListener] && doc[addEventListener](domContentLoaded, fn = function () {
    doc.removeEventListener(domContentLoaded, fn, f)
    flush()
  }, f)


  hack && doc.attachEvent(onreadystatechange, fn = function () {
    if (/^c/.test(doc[readyState])) {
      doc.detachEvent(onreadystatechange, fn)
      flush()
    }
  })

  return (ready = hack ?
    function (fn) {
      self != top ?
        loaded ? fn() : fns.push(fn) :
        function () {
          try {
            testEl.doScroll('left')
          } catch (e) {
            return setTimeout(function() { ready(fn) }, 50)
          }
          fn()
        }()
    } :
    function (fn) {
      loaded ? fn() : fns.push(fn)
    })
});

/**
 * @author oldj
 * @blog http://oldj.net
 */

'use strict';

function NCFloat(el) {
    this.el = el;
    this.init();
}

NCFloat.prototype = {
init: function () {
        var _this = this;
        this.makeOverlay();
        var as = this.el.getElementsByTagName('a');
        var i;
        var el;
        for (i = 0; i < as.length; i ++) {
            el = as[i];
            if (el.className == 'close') {
                el.onclick = function () {
                    _this.hide();
                    return false;
                };
                break;
            }
        }
        
    },
    makeOverlay: function () {
        if (this.el_overlay) return;
        var el = document.createElement('div');
        el.className = 'nc-f-overlay';
        document.body.appendChild(el);
        this.el_overlay = el;
    },
    show: function (callback) {
        this.el_overlay.style.display = 'block';
        this.el.style.display = 'block';

        callback && callback();
    },
    hide: function (keep) {
        this.el_overlay.style.display = 'none';
        this.el.style.display = 'none';
        if (!keep) {
            location.reload();
        }
    }
};
function findParentByTagName(elem, name) {
            while(elem) {
               if ((elem.tagName && elem.tagName.toLowerCase()) === name) {break;}
               elem = elem.parentNode;
            }  
            return elem;
}

function _nc_plugin_init (appkey, renderto_div, insert_id, random_nc_init){
        var random_nc = new noCaptcha();
        random_nc.init({
            renderTo: renderto_div,
            appkey: appkey,
            customWidth: 300,
            closeImage:false,
            scene: 'bbs',
            is_Opt: 1,
            language: 'cn',
            callback: function (data) {
                if(insert_id == 'lostpwsubmit'){
                    var insertparent = document.getElementsByName("lostpwsubmit")[0];
                }else{
                    var insertparent = document.getElementById(insert_id);
                    }
                var wrapper = document.createElement("div");
                wrapper.style.display = 'none';
                wrapper.innerHTML = '<input name = "sessionId" value = ' + data.csessionid  + ' type = "hidden"/>' +
                        '<input name = "sig" value = ' + data.sig  + ' type = "hidden"/>' +
                        '<input name = "_NC" value ='+random_nc_init+'  type = "hidden"/>' +
                        '<input name = "app_token" value = '+umx.getToken()+' type = "hidden"/>';
                insertparent.appendChild(wrapper);
            }
        })
       window[random_nc_init] = random_nc; 
    }
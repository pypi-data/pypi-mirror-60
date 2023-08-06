if(typeof hidden_area==='undefined') {
                hidden_area = $('<div  class="hidden-area"></div>').hide();
                $('body').append(hidden_area);
            }
winjs = function () {
    // var FullScreenSwitch = swjs.FullScreenSwitch;
    var {Switch, FullScreenSwitch, SpeakSwitch} = swjs;
    var {
        genUid, isdefined, makeDraggable, simpleMakeResizable
    } = wpjs;
    const parseCss=function(str){
      // str='';
      str=str.trim();
      if(str.endsWith(';'))str=str.slice(0,str.length-1);
      // console.log("str:",str);
      var dict={};
      var arr=str.split(';');
      arr.forEach((pair)=>{
          var [key,value]=pair.split(':');
          dict[key]=value;
      });
      return dict;
    };
    const createElement=function (tag) {
        var sinTags = [
            'img', 'hr', 'br'
        ];
        var douTags = [
            'div', 'ul', 'li', 'label'
        ];
        if (sinTags.indexOf(tag) > -1) {
            var el = $(`<${tag}></${tag}>`);
        } else {
            var el = $(`<${tag}>`);
        }
        return el.appendTo(hidden_area);
    };
    const wrapText=function(text){
      let el=createElement('textarea');
      el.attr('readonly','true');
      el.width('100%');
      el.height('100%');
      el.css('border','none');
      el.css('overflow-y','visible');
      el.val(text);
      return el
    };
    const wrapHtml=function(text){
      let el=createElement('div');
      el.html(text);
      return el;
    };
    const wrapMarkdown=function(text){
      let el=createElement('div').addClass('markown-box');
      el.html(marked(text));
      return el;
    };
    class RWidget{
        constructor(el,className) {
            if($.isPlainObject(el)){
                el=el.el;
                className=el.className;
            }
            className=className||this.constructor.name||"RWidget";
            el=el || '<div></div>';
            this.id=className+genUid();
            this.el=$(el);
            this.el.addClass(className);
            hidden_area.append(this.el);
            this.el.attr('id',this.id);
            this.visible=true;
        }
        dockLeft(){this.left(0);return this;}
        dockRight(){this.right(0);return this;}
        fitHeight(){
            this.fullHeight();
            this.top(0);
            return this;
        }
        fitWidth(){
            this.fullWidth();
            this.left(0);
            return this;
        }
        fullHeight(){
            this.height('100vh');
            return this;
        }
        fullWidth(){
            this.width('100vw');return this;
        }
        wrapText(text){
            this.setContent(wrapText(text));return this;
        }
        wrapHtml(text){
            this.setContent(wrapHtml(text));return this;
        }
        wrapCode(text,type){
            var pre=createElement('pre');
            var code=createElement('code').addClass('language-'+type);
            pre.append(code);
            text=hljs.highlightAuto(text).value;
            code.html(text);
            console.log("pre:",pre);
            this.setContent(pre);
            return this;
        }
        wrapMarkdown(text){
            this.setContent(wrapMarkdown(text));return this;
        }
        setContent(content){
            this.contentBox.html(content);
            return this;
        }
        disableDefualtCtrlAndThisKeydown(key){
            this.onCtrlAndThisKeydown(key,(e)=>{
                e.preventDefault();
            });return this;
        }
        disableDefaultKeydown(key){
            this.onThisKeydown(key,(e)=>{
                e.preventDefault();
            });return this;
        }
        disableDefaultEvent(eventName){
            this.on(eventName,(e)=>{
                e.preventDefault();
            });return this;
        }
        hover(callback){
            if(!callback){return this.el.hover();}
            this.el.hover(callback);return this;
        }
        click(callback){
            if(!callback){return this.el.click();}
            this.el.click(callback);return this;
        }
        on(types, selector, data, fn ){this.el.on(types, selector, data, fn );return this;}
        onKeydown(callback){this.el.onkeydown(fn);return this;}
        onEnterKeydown(callback){
            this.onThisKeydown(13,callback);return this;
        }
        onTabKeydown(callback){
            return this.onThisKeydown(9,callback);
        }
        onCtrlAndThisKeydown(key,callback){
            this.onCtrlKeydown((e)=>{
                if(e.keyCode===key){
                    if(callback)callback(e);
                }
            });return this;
        }
        onCtrlKeydown(callback){
            this.onKeydown((e)=>{
                if(e.ctrlKey){
                    if(callback)callback(e);
                }
            });return this;
        }
        onThisKeydown(key,callback){
            this.el.onkeydown((e)=>{
                if(e.keyCode===key){
                    if(callback)callback(e);
                }
            });return this;
        }
        simpleMakeResizable(){
            this.css({
                "resize":"both",
                "overflow":"auto"
            });return this;
        }
        setScrollbar(el){
            el=el||this.contentBox||this.el;
            return this;
            var dict=parseCss('scrollbar-face-color:#ffcc99;SCROLLBAR-HIGHLIGHT-COLOR:#ff0000;SCROLLBAR-SHADOW-COLOR:#ffffff;SCROLLBAR-3DLIGHT-COLOR:#000000;SCROLLBAR-ARROW-COLOR:#ff0000;SCROLLBAR-TRACK-COLOR:#dee0ed;SCROLLBAR-DARKSHADOW-COLOR:#ffff00');
            el.css(dict);
            // console.log("css:",dict)
            return this;
            // el[0].style+=``;
            // el[0].style+=`;SCROLLBAR-FACE-COLOR:#ffcc99;SCROLLBAR-HIGHLIGHT-COLOR:#ff0000;SCROLLBAR-SHADOW-COLOR:#ffffff;SCROLLBAR-3DLIGHT-COLOR:#000000;SCROLLBAR-ARROW-COLOR:#ff0000;SCROLLBAR-TRACK-COLOR:#dee0ed;SCROLLBAR-DARKSHADOW-COLOR:#ffff00`;
        }
        makeDraggable(handle){if(!handle)handle=this.handle;makeDraggable(this.el,handle);return this;}
        shadow(){this.el.css('box-shadow','0 9px 46px 8px rgba(0,0,0,.14), 0 11px 15px -7px rgba(0,0,0,.12), 0 24px 38px 3px rgba(0,0,0,.2)');return this;}
        setBackgroundImage(arg){return this.css("background-image",arg)}
        setBackgroundColor(arg){return this.css("background-color",arg)}
        setColor(arg){return this.css("color",arg)}
        setZIndex(arg){return this.css("z-index",arg);}
        getZIndex(){return this.css('z-index')}
        setPosition(top,left){this.top(top);this.left(left)}
        getPosition(){return [this.top(),this.left()]}
        right(arg){return this.css("right",arg)}
        bottom(arg){return this.css("bottom",arg)}
        left(arg){return this.css("left",arg)}
        top(arg){return this.css("top",arg)}
        setSize(w,h){this.width(w);this.height(h);}
        getSize(){return [this.width(),this.height()]}
        height(h){this.el.height(h);return this;}
        width(arg){this.el.width(arg);return this;}
        parseCss(str){var dict=parseCss(str);this.el.css(dict);return this;}
        css(name,value){this.el.css(name,value);return this;};
        attr(name,value){return this.el.attr(name,value)}
        appendTo(el){this.el.appendTo($(el));return this;}
        prependTo(el){this.el.prependTo($(el));return this;}
        find(arg){return this.el.find(arg);}
        invertVisibility(){
            if(this.visible){this.hide();}
            else{this.show();}
            return this;
        }
        remove(){
            this.el.remove();
            return this;
        }
        hide(){
            this.visible=false;
            this.el.hide();
            return this;
        }
        show(){
            this.visible=true;
            this.el.show();
            return this;
        }
    }
    class RButton extends RWidget{
        constructor(content,onclick) {
            super("<button></button>");
            if($.isPlainObject(content)){
                content=content.content;
                onclick=content.onclick;
            }
            if(content)this.el.html(content);
            if(onclick)this.click(onclick);
        }
    }
    class RListbox extends RWidget{
        constructor(...items) {
            super();
            this.width(200);
            this.css({
                "background-color":"blue",
                "color":"white",
                "font":"bold",
                "min-height":"200px"
            });

            var itemList=$("<div></div>");
            this.itemList=itemList;
            this.el.append(itemList);
            items.forEach((item)=>{this.addItem(item)});
        }
        addItem(el){
            // console.log('itemlist:',this.itemList);
            // console.log('el:',$(el));
            this.itemList.append($(el));
            // console.log("new hihih")
        }
    }
    class RMenu extends RWidget{}
    class RDropdownMenu extends RMenu{}
    class RPopupMenu extends RMenu{
        constructor(title,...items) {
            super();
            // console.log('items:',items)
            this.listbox=new RListbox(items);
            var handle=new RButton(title,(e)=>{
                this.listbox.invertVisibility();
            });
            this.handle=handle;
            this.listbox.appendTo(this.el);
            this.handle.appendTo(this.el);
        }

    }
    class RInput extends RWidget{
        constructor(el) {
            super('<input>');
            if($.isPlainObject()){
                if(el.type)this.el.attr("type",el.type);
                if(el.value)this.el.attr("value",el.value);
            }
        }
        type(arg){
            if(arguments.length){
                this.attr("type",arg);
            }else {
                this.attr("type");
            }
        }
    }
    class RTextInput extends RInput{}
    class RFileInput extends RInput{}
    class RDialog extends RWidget{
        constructor() {
            super();
        }
    }
    class RMessagebox extends RDialog{}
    class RInputDialog extends RDialog{
        constructor() {
            super();
            var input=new RInput();
            input.appendTo(this.el);
            this.input=input;
        }
    }
    class RConfirmDialog extends RDialog{
        constructor(callback) {
            super();
            var nb=new RButton("YES");
            nb.click(()=>{this.remove()});
            var yb=new RButton("NO");
            yb.click(()=>{this.remove();if(callback)callback();});
            this.onEnterKeydown(()=>{yb.click()});
        }
    }
    class RTextarea extends RWidget{
        constructor() {
            super("<textarea></textarea>");
        }
    }
    class RImagearea extends RWidget{
        constructor() {
            super("<img>");
        }
    }
    class RWindow extends RWidget{
        constructor() {
            super();
            `<div style="box-shadow: ">`
            this.setSize(500,400);
            this.el[0].style+=`;position:fixed;display:flex;flex-flow:column`;
            this.shadow();
            this.handle=createElement('div').addClass('rwindow-handle').appendTo(this.el);
            this.handle[0].style+=';display:flex;min-height:20px;width:100%;background-color:orange;';
            // this.makeDraggable(this.handle);
            // this.simpleMakeResizable();
            this.contentBox=createElement('div').addClass('rwindow-contentbox').appendTo(this.el);
            this.contentBox[0].style+=`;display:flex;flex:1 0 auto;max-height:100vh;flex-flow:column;overflow:auto`;
            this.el.css('overflow','hidden');
            this.setScrollbar();
        }

    }
    class QWedget {
        constructor(className) {
            className = className || 'QWedget';
            this.uid = className + genUid();
            this.active = false;
            this.visible = true;
            this.onCreate = [];
            // this.appendTo($('body'));
            // this.hide();

        }

        help() {
            var doc = `
            Please re-implement these methods:
                activate()
                source()
            `;
            console.log(doc);
            return doc;
        }

        el() {
            return $("#" + this.uid);
        }

        setSize(width, height) {
            return this.promise(() => {
                if (!this.sizeHistory) this.sizeHistory = [];
                let h = this.el().height();
                let w = this.el().width();
                this.sizeHistory.push([w, h]);
                this.el().width(width);
                this.el().height(height);
            });
        }
        getSize(){
            return [this.el().width(),this.el().height()];
        }
        restoreSize() {
            if (!this.sizeHistory) {
                this.sizeHistory = [];
                return;
            }
            var [w, h] = this.sizeHistory.slice(-1)[0];
            this.el().width(w);
            this.el().height(h);
        }

        find(arg) {
            return this.el().find(arg);
        }

        hide() {
            this.visible = false;
            this.el().hide();
            return this;
        }

        show() {
            this.visible = true;
            this.el().show();
            return this;
        }

        remove() {
            this.el().remove();
            return this;
        }

        promise(func) {
            if (this.active) func();
            else this.onCreate.push(() => {
                func();
            })
        }

        listenEvent(eventName, callback) {
            this.promise(() => {
                this.el().on(eventName, callback);
            });
            return this;
        }

        listenClick(callback) {
            return this.listenEvent("click", callback);
        }

        listenKeydown(key, callback) {
            return this.listenEvent("keydown", (e) => {
                var match = false;
                if (typeof key === "number") {
                    if (e.keyCode === key) match = true;
                } else if (typeof key === "string") {
                    if (e.key === key) match = true;
                }
                if (match) callback(e);
            });
        }

        listenCtrlKeydown(arg1, arg2) {
            if (arguments.length === 2) {
                return this.listenKeydown(arg1, (e) => {
                    if (e.ctrlKey && typeof arg2 === 'function') arg2(e);
                })
            } else {
                return this.listenEvent("keydown", (e) => {
                    if (e.ctrlKey && (typeof arg1 === "function")) arg1(e);
                })
            }
        }

        activate() {
            this.active = true;
            // console.log("activate:",this.el().attr('id'));
            // console.log(this.el())
            for (var i in this.onCreate) {
                if (typeof this.onCreate[i] == 'function') this.onCreate[i]();
            }
            // console.log("The method 'activate' must be re-implemented by subclasses.'");
        }

        hookParent(el) {
            return this.appendTo(el);
        }

        appendTo(el) {
            // console.log("active:", this.active,
            //     this.uid, "appendtTo:", $(el),
            //     "this.el().parent():", this.el().parent());
            if (el) {
                if (this.active) {
                    $(el).append(this.el());
                    return;
                }
                $(el).append($(this.toString()));
            }
            this.activate();
        }

        hook(el) {
            if (el) {
                if (this.active) {
                    $(el).append(this.el());
                    return;
                }
                $(el).replaceWith(this.toString());
            }
            this.activate();
        }

        update() {
            if (this.active) {
                var el = this.el();
                el.replaceWith(this.toString());
                this.activate();
            }
        }

        source() {
            throw "The method 'source()' must be re-implemented bu subclasses.";
            return {
                template: ``,
                style: ``,
                script: ``
            }
        }

        toString() {
            var src = this.source();
            var str = src.template + (src.style || '') + (src.script || '');
            // console.log(str)
            return str;
        }
    }

    // class Q
    class QMenubar extends QWedget {
        constructor(items) {
            super("QMenubar");
            this.items = [];
            if (isdefined(items)) {
                var keys = Object.keys(items);
                for (var k in keys) {
                    this.addItem(k, items[k]);
                }
            }
        }

        itemsToString() {
            var s = '';
            this.items.map((v, i) => {
                s += v;
            });
            return s;
        }

        addItem(name, callback) {
            var item = this.newItem(name, callback);
            this.items.push(item);
            console.log("add item", item)
        }

        newItem(name, callback) {
            var cbname = `callback_${genUid()}`;
            window[cbname] = callback;
            var el = `<span onclick="${cbname}()" class="label-public menu-item">${name}</span>`;
            return el;
        }

        source() {
            return {
                template:
                    `\
            <div class="text-info qmenubar" id="${this.uid}">
            ${this.itemsToString()}
        </div>\
            `,
                style:
                    `\
                <style>
                 #${this.uid} {
            flex: 0 1 40px;
            width: 100%;
            background-color: white;color: orange;
            /*border-bottom: black dotted 2px;*/
        }
        #${this.uid} .menu-item{
            margin:auto 3px auto 3px;
            border-top: dotted black 2px;
            border-left: dotted black 2px;
            border-right: dotted black 2px;
            border-bottom: dotted black 2px;
        }\
            </style>\
                `
            }
        }
    }

    emitQEvent = function (name, params) {
        dispatchEvent(new CustomEvent("qevent-" + name, {
            detail: params
        }));
    };

    class QDialog extends QWedget {
        constructor(content) {
            super("Dialog");
            if ($.isPlainObject(content)) {
                var obj = content;
                this.content = obj.content;
            } else if (typeof content != "undefined") {
                this.content = content;
            }

        }

        activate() {
            var dialog=this.el().find("dialog")[0];
            // if (! dialog.showModal) {
      // dialogPolyfill.registerDialog(dialog);
    // }
    //         dialog.showModal();
            this.active = true;
            var el = this.el();
            el.find(".handle-close").click(() => {
                el.remove();
            });

        }

        close() {
            return this.remove();
        }

        setContent(content) {
            this.content = content;
            this.update();
        }

        getContent() {
            if (!this.content) return '';
            else return this.content;
        }

        source() {
            return {
                template:
                    `
<div id="${this.uid}">
            <div class="head"><span class="handle-close">✖</span></div>
            <div class="body">${this.getContent()} <dialog class="mdl-dialog">
    <h4 class="mdl-dialog__title"></h4>
    <div class="mdl-dialog__content">
      <p>
      ${this.getContent()}
      </p>
    </div>
<!--    <div class="mdl-dialog__actions">-->
<!--      <button type="button" class="mdl-button">Agree</button>-->
<!--      <button type="button" class="mdl-button close">Disagree</button>-->
<!--    </div>-->
  </dialog></div>
           
</div>
            `,
                style:
                    `
                <style>
            #${this.uid} .head{
                display: flex;flex-flow: row-reverse;
            }
            #${this.uid}{
            display: block;
            width: 100%;
            min-height: 100px;
            /*z-index: 10;*/
            /*    background-color:darkgray;*/
                box-shadow: 0 9px 46px 8px rgba(0,0,0,.14), 0 11px 15px -7px rgba(0,0,0,.12), 0 24px 38px 3px rgba(0,0,0,.2);
            }
            
</style>
                `
            }
        }
    }

    class QWindow extends QWedget {
        constructor(title, width, height, content) {
            super("QWindow");
            if ($.isPlainObject(title)) {
                var el = title;
                this.title = el.title;
                this.init_width = el.width;
                this.init_height = el.height;
                this.init_content = el.content;
            } else {
                this.title = title;
                this.init_width = width;
                this.init_height = height;
                this.init_content = content;
            }
            this.title = this.title || 'Window';
            this.init_width = this.init_width || 450;
            this.init_height = this.init_height || 400;
            this.init_content = this.init_content || '';
            this.left = 0;
            this.top = 0;
            this.zIndex = 1;
            this.init();
        }

        init() {
            var self = this;
            this.doClose = function (e) {
                self.remove();
            };
            this.doMinimize = function (e) {
                self.hide();
            };
            this.doMaximize = function (e) {
                self.setSize("100%", "100%");
                self.setPosition(0, 0);
            };
            this.doRestore = function (e) {
                self.restoreSize();
                self.restorePosition();
            }
        }

        activate() {
            super.activate();
            var self = this;
            simpleMakeResizable(this.el()[0]);
            makeDraggable(this.el()[0], this.getHead()[0]);
            this.el().find('.window-close').click(function () {
                self.close();
            });
            this.el().find('.window-minimize').click(function () {
                self.minimize();
            });
            new Switch(this.el().find('.window-fullscreen'), () => {
                this.maximize()
            }, () => {
                this.restore()
            });
            // new FullScreenSwitch(this.el().find('.window-fullscreen'), this.el());
        }

        close() {
            this.doClose();
        }

        minimize() {
            this.doMinimize();
        }

        maximize() {
            this.doMaximize();
        }

        restore() {
            this.doRestore();
        }


        inputFile(msg, callback) {
            return this.input(msg, callback, 'file');
        }

        inputText(msg, callback, placeHolder = "input text...", defaultValue = '') {
            if ($.isPlainObject(msg)) {
                var {msg, callback, type, placeHolder, defaultValue} = msg;
            }
            return this.input(msg, callback, 'text', placeHolder, defaultValue);
        }

        input(msg, callback, type, placeHolder = "input", defaultValue = '') {
            if ($.isPlainObject(msg)) {
                var {msg, callback, type, placeHolder, defaultValue} = msg;
            }
            type = type || 'text';
            var content = `
            <div style="text-align: center">
            <label >${msg}</label>
            <input class="input" type="${type}" multiple="multiple" placeholder="${placeHolder}" value="${defaultValue}">
            <button class="btn-submit">submit</button>
</div>
            `;
            var dialog = this.dialog(content);
            dialog.el().find(".btn-submit").click(() => {
                var input = dialog.el().find(".input");
                if (type === 'file') {
                    callback(input.val(), input[0].files);
                } else {
                    callback(input.val());
                }
                dialog.remove();
            });
            $(document).keydown((e) => {
                if (e.keyCode === 13) {
                    dialog.el().find(".btn-submit").click();
                }
            })

        }

        confirm(msg, callback) {
            var content = `
                <div style="text-align: center"><label>${msg}</label></div>
                <div style="text-align: center">
                <button class="btn-yes">YES</button><button class="btn-no">NO</button>
</div>
            `;
            var dialog = this.dialog(content);
            $(document).keydown((e) => {
                if (e.keyCode === 13) {
                    dialog.el().find(".btn-yes").click();
                }
            });
            dialog.el().find(".btn-yes").click((e) => {
                if (callback) {
                    callback()
                }
                dialog.remove();
            });
            dialog.el().find(".btn-no").click((e) => {
                dialog.remove();
            })
        }

        success(msg) {
            return this.msg(msg);
        }

        warn(msg) {
            return this.msg(msg);
        }

        info(msg) {
            return this.msg(msg);
        }

        msg(msg) {
            var content = `
                <div style="text-align: center"><label>${msg}</label></div>
                <div style="text-align: center" class="btn-ok" onclick="">OK</div>
            `;
            var dialog = this.dialog(content);
            dialog.el().find(".btn-ok").click((e) => {
                dialog.close();
            });
            $(document).keydown((e) => {
                if (e.keyCode === 13) {
                    dialog.el().find(".btn-ok").click();
                }
            })
        }

        dialog(content) {
            var dialog = new QDialog();
            dialog.setContent(content);
            dialog.appendTo(this.getDialog());
            return dialog;
        }

        getHead() {
            return this.el().find(".qwindow-head");
        }

        getDialog() {
            return this.el().find(".qwindow-dialog");
        }

        clearDialog() {
            this.getDialog().html("");
        }

        getBody() {
            return this.el().find(".qwindow-body");
        }

        getInner() {
            return this.getBody().find(".qwindow-inner");
        }

        setTitle(title) {
            this.promise(() => {
                this.find(".qwindow-title").html(title);
            })
        }

        getTitle() {
            if (this.active) {
                return this.find(".qwindow-title").html();
            }
        }

        setContent(content) {
            this.promise(() => {
                this.getInner().html(content);
            });
            return this;
        }

        getContent() {
            if (!this.active) {
                return this.init_content;
            } else {
                return this.getInner().html();
            }
        }

        setPosition(x, y) {
            if (!this.positionHistory) this.positionHistory = [];
            this.positionHistory.push(this.getPosition());
            this.left = x;
            this.top = y;
            if (this.active) {
                this.el()[0].style.left = x + "px";
                this.el()[0].style.top = y + "px";
            }
        }

        restorePosition() {
            if (!this.positionHistory) {
                this.positionHistory = [];
                return;
            }
            let [x, y] = this.positionHistory.slice(-1)[0];
            this.setPosition(x, y);
        }

        getPosition() {
            if (this.active) {
                return [this.el()[0].offsetLeft, this.el()[0].offsetTop];
            } else {
                return [this.left, this.top];
            }
        }

        setZIndex(zIndex) {
            this.promise(() => {
                this.zIndex = zIndex;
                this.el()[0].style.zIndex = zIndex;
            })
        }

        getZIndex() {
            if (this.active) return Number.parseInt(this.el().css("z-index"));
            else return Number.parseInt(this.zIndex);
        }

        source() {
            return {
                template:
                    `
                <div id="${this.uid}">
                <div class="qwindow-head">
                <span class="qwindow-bar window-close">☒</span>
        <span class="qwindow-bar window-fullscreen"><span class=" switch-on">☐</span><span class="switch-off">❐</span></span>
        <span class="qwindow-bar window-minimize">▣</span>
        <span class="qwindow-title">${this.title}</span>
</div>
                <div class="qwindow-dialog">
                
</div>
                <div class="qwindow-body">
                <div class="qwindow-inner">
                ${this.getContent()}          
</div>
</div>


<style>
           #${this.uid} .qwindow-head{
           display: block;
           }
    #${this.uid} .qwindow-title{
            font-family:Arial, Helvetica, sans-serif;
           font-weight: bold;
           display: flex;flex-flow: row;flex: 1 1 200px;margin-left: 5px;color: whitesmoke;
    }
    #${this.uid} .qwindow-bar{
           margin: auto 3px auto 3px;
    }
    #${this.uid} {
        /*background-color: #ff4a37;*/
        background-color: white;
        width: ${this.init_width}px;
        height: ${this.init_height}px;
        display: flex;
        flex-flow: column;
        resize:both;
        overflow: auto;
        position: absolute;
        left: ${this.left}px;
        top: ${this.top}px;
        z-index: ${this.zIndex};
    }
    #${this.uid}  .qwindow-head {
        flex: 0 0 30px;
        background-color: deepskyblue;
        width: 100%;
        display: flex;
        flex-flow: row-reverse;
    }

    #${this.uid}  .qwindow-body {
        flex: auto;
        overflow: auto;
        padding: 5px;
        width: 100%;
        /*background-color: #f1f1f1;*/
        background-color: hsla(0,0%,58.8%,0.3);

    }

    #${this.uid}  .qwindow-inner {
        box-shadow: 0px 3px 3px -2px rgba(0,0,0,0.2), 0px 3px 4px 0px rgba(0,0,0,0.14), 0px 1px 8px 0px rgba(0,0,0,0.12)
        box-sizing: border-box;
        overflow: auto;
        flex: 1 0 auto;
        height: 100%;
        width: 100%;
        background-color: white;
        padding: 5px;
        border-radius: 4px;
    }
</style>
           
</div>


                `,
                style:
                    `
             `
            }
        }
    }


    return {
        RWidget,RButton,RInput,RTextInput,RFileInput,
        RDialog,RMessagebox,RInputDialog,RListbox, RMenu,
        RDropdownMenu,RImagearea,RTextarea,RWindow,RPopupMenu,

        QWedget: QWedget,
        QDialog: QDialog,
        QMenubar: QMenubar,
        QWindow: QWindow
    }
}();
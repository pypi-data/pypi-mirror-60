ace.define("ace/mode/maze_highlight_rules",["require","exports","module","ace/lib/oop","ace/mode/text_highlight_rules"],function(e,t,n){"use strict";var r=e("../lib/oop"),i=e("./text_highlight_rules").TextHighlightRules,s=function(){this.$rules={start:[{token:"keyword.control",regex:/##|``/,comment:"Wall"},{token:"entity.name.tag",regex:/\.\./,comment:"Path"},{token:"keyword.control",regex:/<>/,comment:"Splitter"},{token:"entity.name.tag",regex:/\*[\*A-Za-z0-9]/,comment:"Signal"},{token:"constant.numeric",regex:/[0-9]{2}/,comment:"Pause"},{token:"keyword.control",regex:/\^\^/,comment:"Start"},{token:"keyword.control",regex:/\(\)/,comment:"Hole"},{token:"support.function",regex:/>>/,comment:"Out"},{token:"support.function",regex:/>\//,comment:"Ln Out"},{token:"support.function",regex:/<</,comment:"In"},{token:"keyword.control",regex:/--/,comment:"One use"},{token:"constant.language",regex:/%[LRUDNlrudn]/,comment:"Direction"},{token:["entity.name.function","keyword.other","keyword.operator","keyword.other","keyword.operator","constant.numeric","keyword.operator","keyword.other","keyword.operator","constant.numeric","string.quoted.double","string.quoted.single"],regex:/([A-Za-z][A-Za-z0-9])( *-> *)(?:([-+*\/]=)( *)((?:-)?)([0-9]+)|(=)( *)(?:((?:-)?)([0-9]+)|("[^"]*")|('[^']*')))/,comment:"Assignment function"},{token:["entity.name.function","keyword.other","keyword.control","keyword.other","keyword.operator","keyword.other","keyword.operator","constant.numeric","entity.name.tag","keyword.other","keyword.control","keyword.other","constant.language","keyword.other","keyword.control","keyword.other","constant.language"],regex:/([A-Za-z][A-Za-z0-9])( *-> *)(IF|if)( *)(?:([<>]=?|==)( *)((?:-)?)([0-9]+)|(\*[\*A-Za-z0-9]))( *)(THEN|then)( *)(%[LRUDNlrudn])(?:( *)(ELSE|else)( *)(%[LRUDNlrudn]))?/,comment:"Equality Function"},{token:"entity.name.function",regex:/[A-Za-z][A-Za-z0-9]/,comment:"Function cell"},{token:"comment.line.double-slash",regex:/ *\/\/.*/,comment:"Comment"}]},this.normalizeRules()};s.metaData={fileTypes:["mz"],name:"Maze",scopeName:"source.maze"},r.inherits(s,i),t.MazeHighlightRules=s}),ace.define("ace/mode/folding/cstyle",["require","exports","module","ace/lib/oop","ace/range","ace/mode/folding/fold_mode"],function(e,t,n){"use strict";var r=e("../../lib/oop"),i=e("../../range").Range,s=e("./fold_mode").FoldMode,o=t.FoldMode=function(e){e&&(this.foldingStartMarker=new RegExp(this.foldingStartMarker.source.replace(/\|[^|]*?$/,"|"+e.start)),this.foldingStopMarker=new RegExp(this.foldingStopMarker.source.replace(/\|[^|]*?$/,"|"+e.end)))};r.inherits(o,s),function(){this.foldingStartMarker=/(\{|\[)[^\}\]]*$|^\s*(\/\*)/,this.foldingStopMarker=/^[^\[\{]*(\}|\])|^[\s\*]*(\*\/)/,this.singleLineBlockCommentRe=/^\s*(\/\*).*\*\/\s*$/,this.tripleStarBlockCommentRe=/^\s*(\/\*\*\*).*\*\/\s*$/,this.startRegionRe=/^\s*(\/\*|\/\/)#?region\b/,this._getFoldWidgetBase=this.getFoldWidget,this.getFoldWidget=function(e,t,n){var r=e.getLine(n);if(this.singleLineBlockCommentRe.test(r)&&!this.startRegionRe.test(r)&&!this.tripleStarBlockCommentRe.test(r))return"";var i=this._getFoldWidgetBase(e,t,n);return!i&&this.startRegionRe.test(r)?"start":i},this.getFoldWidgetRange=function(e,t,n,r){var i=e.getLine(n);if(this.startRegionRe.test(i))return this.getCommentRegionBlock(e,i,n);var s=i.match(this.foldingStartMarker);if(s){var o=s.index;if(s[1])return this.openingBracketBlock(e,s[1],n,o);var u=e.getCommentFoldRange(n,o+s[0].length,1);return u&&!u.isMultiLine()&&(r?u=this.getSectionRange(e,n):t!="all"&&(u=null)),u}if(t==="markbegin")return;var s=i.match(this.foldingStopMarker);if(s){var o=s.index+s[0].length;return s[1]?this.closingBracketBlock(e,s[1],n,o):e.getCommentFoldRange(n,o,-1)}},this.getSectionRange=function(e,t){var n=e.getLine(t),r=n.search(/\S/),s=t,o=n.length;t+=1;var u=t,a=e.getLength();while(++t<a){n=e.getLine(t);var f=n.search(/\S/);if(f===-1)continue;if(r>f)break;var l=this.getFoldWidgetRange(e,"all",t);if(l){if(l.start.row<=s)break;if(l.isMultiLine())t=l.end.row;else if(r==f)break}u=t}return new i(s,o,u,e.getLine(u).length)},this.getCommentRegionBlock=function(e,t,n){var r=t.search(/\s*$/),s=e.getLength(),o=n,u=/^\s*(?:\/\*|\/\/|--)#?(end)?region\b/,a=1;while(++n<s){t=e.getLine(n);var f=u.exec(t);if(!f)continue;f[1]?a--:a++;if(!a)break}var l=n;if(l>o)return new i(o,r,l,t.length)}}.call(o.prototype)}),ace.define("ace/mode/maze",["require","exports","module","ace/lib/oop","ace/mode/text","ace/mode/maze_highlight_rules","ace/mode/folding/cstyle"],function(e,t,n){"use strict";var r=e("../lib/oop"),i=e("./text").Mode,s=e("./maze_highlight_rules").MazeHighlightRules,o=e("./folding/cstyle").FoldMode,u=function(){this.HighlightRules=s,this.foldingRules=new o};r.inherits(u,i),function(){this.lineCommentStart="//",this.$id="ace/mode/maze"}.call(u.prototype),t.Mode=u})
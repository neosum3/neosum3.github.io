//Javascript for fgo.html
//Not in use because cannot pass value from flask (python) by render to a seperate file

//<script>
        (function(W){
            var sets = []; //object to put in everything
            var CN_form = 0, US_note= 1;
            var D, count;
            function init(){
                D=W.document;
                count = 2; //for CN and US
                for (var i = 0; i < count; i++){
                    var temp = D.getElementsByTagName('form')[i];
                    //console.log(D.getElementsByTagName('form'));
                    sets.push({
                        form : temp,
                        bts : temp.getElementsByTagName('button'),
                        ipt : temp.getElementsByTagName('input'),
                        prev : []
                    });
                    sets[i].form.addEventListener('submit',save, false);
                    sets[i].bts[1].addEventListener('click',cancel, false);
                    sets[i].bts[2].addEventListener('click',edit,false);
                }
                W.document.getElementById('CN_stone_total').innerHTML="{{CN_info['quartz']+3*CN_info['ticket']}}";
                W.document.getElementById('CN_draw').innerHTML="{{(CN_info['quartz']+3*CN_info['ticket'])//3}}";
                sets[CN_form].ipt[0].value="{{CN_info['act_time']}}";
                sets[CN_form].ipt[1].value="{{CN_info['guild1']}}"; //make invisible later?
                sets[CN_form].ipt[2].value="{{CN_info['guild1_link']}}";  //*
                if("{{CN_info['guild1_link']}}" == "") W.document.getElementById('CN_guild1_box').innerHTML= "{{CN_info['guild1']}}"; //no link input
                else W.document.getElementById('CN_guild1_box').innerHTML="<a href= '{{CN_info['guild1_link']}}'> {{CN_info['guild1']}} </a> ";
                sets[CN_form].ipt[3].value="{{CN_info['guild2']}}";
                //W.document.getElementById('CN_guild2_box').innerHTML="<a href='{{CN_info['guild2_link']}}'> {{CN_info['guild2']}} </a> ";
                sets[CN_form].ipt[4].value="{{CN_info['weekly']}}";
                //W.document.getElementById('CN_weekly_box').innerHTML="<a href='{{CN_info['weekly_link']}}'> {{CN_info['weekly']}} </a> ";
                sets[CN_form].ipt[5].value="{{CN_info['quartz']}}";   //*
                sets[CN_form].ipt[6].value="{{CN_info['ticket']}}";   //*
                sets[CN_form].ipt[7].value= "{{CN_info['note']}}";
                sets[US_note].ipt[0].value= "{{US_info['note']}}";
                console.log(sets);
                getWidth();
            }

            function save(e){
                event.preventDefault();  //The default action of the event will not be triggered.For example, clicked anchors will not take the browser to a new URL.
                //console.log(sets);//console.log(this); //console.log(this.id);
                var id;
                if(this.id == "US_note")  {
                    id = US_note;
                    $.getJSON("/fgo",  {US_data: $("#US_data").val()}, function(data, textStatus, jqXHR) {console.log(data);});
                }
                else if(this.id == "CN_form") {
                    id = CN_form;
                    if( !isPosInt($("#CN_stone_data").val()) || !isPosInt($("#CN_ticket").val())){
                        alert("Please input valid number"); //make sure input is integer>=0
                        return false;
                    }
                    if( !is_url($("#CN_guild1_link").val()) & $("#CN_guild1_link").val() != ""){
                        alert("Please enter valid url"); //make sure input is integer>=0
                        return false;
                    }
                    sets[id].ipt[2].value = addhttp($("#CN_guild1_link").val());
                    sets[id].ipt[5].value = parseInt($("#CN_stone_data").val());  //display number as integeter, not 09 or 5.0, etc
                    sets[id].ipt[6].value = parseInt($("#CN_ticket").val());
                    $.getJSON("/fgo",  {
                        CN_act_time: $("#CN_act_time").val(),
                        CN_guild1: $("#CN_guild1").val(),
                        CN_guild1_link: $("#CN_guild1_link").val(),
                        CN_guild2: $("#CN_guild2").val(),
                        CN_weekly: $("#CN_weekly").val(),
                        CN_stone: $("#CN_stone_data").val(),
                        CN_ticket: $("#CN_ticket").val(),
                        CN_note: $("#CN_note").val()
                    }, function(data, textStatus, jqXHR) {console.log(data);});
                    if($("#CN_guild1_link").val() == "") W.document.getElementById('CN_guild1_box').innerHTML= $("#CN_guild1").val(); //no link input
                    else W.document.getElementById('CN_guild1_box').innerHTML='<a href= ' + $("#CN_guild1_link").val() + '>'+ $("#CN_guild1").val() +'</a>';
                    W.document.getElementById('CN_stone_total').innerHTML=parseInt($("#CN_stone_data").val())+3*parseInt($("#CN_ticket").val());
                    W.document.getElementById('CN_draw').innerHTML=Math.floor((parseInt($("#CN_stone_data").val())+3*parseInt($("#CN_ticket").val()))/3);
                }
                sets[id].form.classList.remove('invert');
                var l=sets[id].ipt.length;
                while(l--){
                    sets[id].ipt[l].readOnly=true;
                };
                for (var i = 0; i < count; i++) sets[i].previous = [];
            }
            function edit(e){
                e.preventDefault();
                var id;
                console.log(this);
                if(this.id == "US_note_edit") id = US_note;
                else if(this.id == "CN_edit") id = CN_form;
                sets[id].form.classList.add('invert');
                var l=sets[id].ipt.length;
                while(l--){   //if (l = i - 1) is bigger than 0
                    sets[id].prev[l]=sets[id].ipt[l].value;
                    sets[id].ipt[l].readOnly=false;
                }
                getWidth();
            }
            function cancel(e){
                e.preventDefault();
                var id;
                console.log(this);
                if(this.id == "US_note_cancel") id = US_note;
                else if(this.id == "CN_cancel") id = CN_form;
                sets[id].form.classList.remove('invert');
                var l=sets[id].ipt.length;
                while(l--){
                    sets[id].ipt[l].value=sets[id].prev[l];
                    sets[id].ipt[l].readOnly=true;
                }
                getWidth();
            }
        W.addEventListener('load',init,false);
        })(window)

        function isInt(value) { //checks whether input is int or 'int', see https://stackoverflow.com/questions/14636536/how-to-check-if-a-variable-is-an-integer-in-javascript
            var x = parseFloat(value);
            return !isNaN(value) && (x | 0) === x; //bitwise  check
        }
        function isPosInt(value){  //pos & 0
            if(!isInt(value)) return false;
            var x = parseInt(value);
            if(x>=0) return true;
            return false;
        }
        function is_url(str)  //check url is valid or not
        {
            var regexp =  /^(?:(?:https?|ftp):\/\/)?(?:(?!(?:10|127)(?:\.\d{1,3}){3})(?!(?:169\.254|192\.168)(?:\.\d{1,3}){2})(?!172\.(?:1[6-9]|2\d|3[0-1])(?:\.\d{1,3}){2})(?:[1-9]\d?|1\d\d|2[01]\d|22[0-3])(?:\.(?:1?\d{1,2}|2[0-4]\d|25[0-5])){2}(?:\.(?:[1-9]\d?|1\d\d|2[0-4]\d|25[0-4]))|(?:(?:[a-z\u00a1-\uffff0-9]-*)*[a-z\u00a1-\uffff0-9]+)(?:\.(?:[a-z\u00a1-\uffff0-9]-*)*[a-z\u00a1-\uffff0-9]+)*(?:\.(?:[a-z\u00a1-\uffff]{2,})))(?::\d{2,5})?(?:\/\S*)?$/;
            if (regexp.test(str)){
              return true;
            }
            else{
              return false;
            }
        }
        function addhttp(url) {  //Make url start with http (if not will get error)
            if (url=="") return url; //don't change empty url
            if (!/^(f|ht)tps?:\/\//i.test(url)) {
                url = "http://" + url;
            }
            return url;
        }
        function getWidth(){//***For auto adjust input box size********
            $.fn.textWidth = function(text, font) {
                if (!$.fn.textWidth.fakeEl) $.fn.textWidth.fakeEl = $('<span>').hide().appendTo(document.body);
                $.fn.textWidth.fakeEl.text( this.val() || this.text() ).css('font', font || this.css('font'));
                return $.fn.textWidth.fakeEl.width();
            };
            $('.width-dynamic').on('input', function() {
                var inputWidth = $(this).textWidth() + 15;
                $(this).css({
                    width: inputWidth
                })
            }).trigger('input');
            function inputWidth(elem, minW, maxW) {
                elem = $(this) ;
                console.log(elem)
            }
            var targetElem = $('.width-dynamic');
            inputWidth(targetElem);
        }
   // </script>
/******************************************************************************
 * 
 */
$.fn.yVal = function(pValue)
{
    if ($(this).length !== 0) 
    {
        var tag = $(this)[0].localName.toLowerCase();
        var type = $(this)[0].type.toLowerCase();

        if (tag === 'input')
        {
            if (type === 'radio'.toLowerCase())
            {
                if (pValue === '')
                {
                    $(this).attr('checked', false);
                    $(this).parent().removeClass('active');
                }
                else 
                { 
                    $(this).parent().find('input:radio[value='+pValue+']').click();
                }
            }
            else
            {
                $(this).val(pValue);
            }
        }
        else if (tag === 'select')
        {
            $(this).val(pValue).change();
        }
    }
}

/******************************************************************************
 * 
 */
$.fn.yDisabled = function(pValue = true)
{
    var type = $(this)[0].type.toLowerCase();

    $(this).attr('disabled', pValue);

    if (type === 'radio'.toLowerCase())
    {
        if (pValue) {
            $(this).parent().addClass('disabled');
        } else {
            $(this).parent().removeClass('disabled');
        }
    }
}

/******************************************************************************
 * 
 */
$.fn.yReadonly = function(pValue = true)
{
    var type = $(this)[0].type.toLowerCase();

    $(this).attr('readonly', pValue);

    if (type === 'radio'.toLowerCase())
    {
        if (pValue) {
            // $(this).parent().addClass('readonly');
            $(this).parent().addClass('disabled');
        } else {
            // $(this).parent().removeClass('readonly');
            $(this).parent().removeClass('disabled');
        }
    }
}

$.fn.hideZero = function() {
    return this.each(function() {
        $('.nozero', this).each(function() {
			  let text = $(this).text();
			  text = text.replaceAll(",", "");
			  if(parseInt(text) == 0){
				  $(this).text("");
			  }
        });
    });
};

$.fn.brokenWord = function(colIdx, isStats) {
    return this.each(function() {
        $('tr', this).each(function(row) {
            $('td', this).eq(colIdx).each(function(col) {
				let text = $(this).text();
				$(this).html([...text].join("<br>"));
            });
        });
    });
};
$.fn.yRowClass = function(colIdx, _className, isStats) {
    return this.each(function() {
		var length = $('tr', this).length;
        $('tr', this).each(function(row) {
            $('td', this).eq(colIdx).each(function(col) {
				if($(this).is(':visible')){
					if(row+parseInt($(this).attr("rowspan")) != length)
						$(this).addClass(_className);
				}
            });
        });
    });
};
$.fn.yRowClassNext = function(colIdx, _className, isStats) {
    return this.each(function() {
		var rowspans = [];
        $('tr', this).each(function(row) {
			var rowspan = 0;
			$('td', this).eq(colIdx).each(function(col) {
				if($(this).is(':visible')){
					rowspan = $(this).attr("rowspan");
                    if(rowspan == "" || rowspan == undefined){
                        rowspan = 1;
                    }
				}
			});
			if(rowspan > 0){
				rowspans.push(row+parseInt(rowspan));
			}
        });
		var _ = 0;
        $('tr', this).each(function(row) {
			if(row == (parseInt(rowspans[_])-1)){
				for (let idx = colIdx + 1; idx < $(this).find('td').length; idx++) {
					$('td', this).eq(idx).each(function (col) {
						$(this).addClass(_className);
					});
				}
				_++;
			}
		});

    });
};
$.fn.calculation = function(colStart, colEnd) {
	let result = [];
	for(let idx=colStart;idx <= colEnd;idx++) {
		result.push(0);
	}
    this.each(function() {
		var i = 0;
		for(let idx=colStart;idx <= colEnd;idx++){
            if($(this).find("td").eq(idx).css("display") !== "none"){
                var count =  $(this).find("td").eq(idx).text().replaceAll(",", "");
                result[i] += (count == "" ? 0 : parseInt(count));

            }
            i++;
		}

    });
	return result;
};

$.fn.widthMatch = function() {
    var maxWidth = 0;
    this.each(function() {
        let width = parseInt($(this).css("width").replace("px", "")) | 0;
        if(maxWidth < width){
            maxWidth = width;
        }
    });
    this.each(function() {
        let style = $(this).attr("style");
        if(style == undefined){
            style = '';
        }
        $(this).attr("style", style+`min-width:${maxWidth}px!important;`);
    });
};
$.fn.widthMatchTarget = function(target) {
    var maxWidth = 0;
    $.each(target, function(pIndex, pValue){
        var width = parseInt($(pValue).css("width").replace("px", "")) | 0;
        maxWidth += width;
        let style = $(pValue).attr("style");
        if(style == undefined){
            style = '';
        }
        $(pValue).attr("style", style+`width:${width}px!important;`);
    })
    if(target.length > 1){
        maxWidth -= 2;
    }
    this.each(function() {
        let style = $(this).attr("style");
        if(style == undefined){
            style = '';
        }
        $(this).attr("style", style+`min-width:${maxWidth}px!important;max-width:${maxWidth}px!important;`);
    });
};

$.fn.serializeObject = function() {
    var obj = null;
    try {
        if (this[0].tagName && this[0].tagName.toUpperCase() == "FORM") {
            var arr = this.serializeArray();
            if (arr) {
                obj = {};
                jQuery.each(arr, function() {
                    if(this.name.endsWith("[]")){
                        if(!obj.hasOwnProperty(this.name))
                            obj[this.name] = [];
                        obj[this.name].push(this.value);
                    }
                    else{
                        obj[this.name] = this.value;
                    }
                });
            }//if ( arr ) {
        }
    } catch (e) {
        alert(e.message);
    } finally {
    }

    return obj;
};


$.fn.yRowspanConditional = function(stIdx, colIdx, isStats) {
    return this.each(function() {
        var that;
        $('tr', this).each(function(row) {
            // visible 속성이 부모 태그의 속성을 따라가기 때문에 레이어 팝업에서 호출할 경우
            // 전처리 이벤트가 아닌 후처리 이벤트에서 호출해야 함
            $('td', this).eq(colIdx).attr("rowspan", $('td', this).eq(stIdx).attr("rowspan"));
            $('td', this).eq(colIdx).css("display", $('td', this).eq(stIdx).css("display"));

            // $('td', this).eq(colIdx).each(function(col) {
            //     $(that).attr("rowspan");
            // });
            // $('td', this).eq(colIdx).each(function(col) {
            //     $(that).attr("rowspan");
            // });
        });
    });
};

$.dateDiff = function(daystring) {
    let now = new Date();
    now.setHours(0,0,0,0);
    let day = new Date(daystring);
    day.setHours(0,0,0,0);
    let Difference_In_Time = now.getTime() - day.getTime();
    let Difference_In_Days = Difference_In_Time / (1000 * 3600 * 24);
    return Difference_In_Days;
};
/******************************************************************************
 * 같은 값이 있는 열을 병합함  
 *   
 * 사용법 : $('#테이블 ID').yRowspan(0);
 */

$.fn.yRowspan = function(colIdx, isStats) {
    return this.each(function() {
        var that;
        $('tr', this).each(function(row) {
            // visible 속성이 부모 태그의 속성을 따라가기 때문에 레이어 팝업에서 호출할 경우 
            // 전처리 이벤트가 아닌 후처리 이벤트에서 호출해야 함
            // $('td', this).eq(colIdx).filter(':visible').each(function(col) { 
            $('td', this).eq(colIdx).each(function(col) {
                if ( $(this).html() == $(that).html() && (!isStats || isStats && $(this).prev().html() == $(that).prev().html()) ) {              
                    rowspan = $(that).attr("rowspan") || 1;
                    rowspan = Number(rowspan)+1;
                    $(that).attr("rowspan",rowspan);

                    // do your action for the colspan cell here
                    $(this).hide();

                    //$(this).remove();
                    // do your action for the old cell here
                } else {
                    that = this;
                }
                // set the that if not already set
                that = (that == null) ? this : that;
            });
        });
    });
};

/******************************************************************************
 * 같은 값이 있는 행을 병합함  
 *   
 * 사용법 : $('#테이블 ID').yColspan(0);
 */     
$.fn.yColspan = function(rowIdx) {
    return this.each(function() {
        var that;
        $('tr', this).filter(":eq("+rowIdx+")").each(function(row) {
            // visible 속성이 부모 태그의 속성을 따라가기 때문에 레이어 팝업에서 호출할 경우 
            // 전처리 이벤트가 아닌 후처리 이벤트에서 호출해야 함 
            // $(this).find('td').filter(':visible').each(function(col) { 
            $(this).find('td').each(function(col) {
                if ($(this).html() == $(that).html()) {
                    colspan = $(that).attr("colSpan");
                    if (colspan == undefined) {
                        $(that).attr("colSpan",1);
                        colspan = $(that).attr("colSpan");
                    }
                    colspan = Number(colspan)+1;
                    $(that).attr("colSpan",colspan);
                    $(this).hide(); // .remove();
                } else {
                    that = this;
                }
                // set the that if not already set
                that = (that == null) ? this : that;
            });
        });
    });
};

/**************************************************************************
 * 
 */
if (typeof $.yawn === 'undefined') {
    $.yawn = {};
}
$.yawn.utils = {};
$.yawn.utils.getSysDate = function() {
    
    var time = new Date();
    time.setUTCHours(time.getUTCHours()+9);
    var year = time.getUTCFullYear();
    var month = time.getUTCMonth()+1;
    var day = time.getUTCDate();
    var hday = -1;
    console.log('yawn.utils.getSysDate', time.getUTCDay());
    if (time.getUTCDay() === 1) {
        hday = '월요일';
    } else if (time.getUTCDay() === 2) {
        hday = '화요일';
    } else if (time.getUTCDay() === 3) {
        hday = '수요일';
    } else if (time.getUTCDay() === 4) {
        hday = '목요일';
    } else if (time.getUTCDay() === 5) {
        hday = '금요일';
    } else if (time.getUTCDay() === 6) {
        hday = '토요일';
    } else if (time.getUTCDay() === 0) {
        hday = '일요일';
    }
    
    return month+'/'+day+' '+hday;
};

/**************************************************************************
 * 
 */
$.yawn.utils.getSysTime = function() {
    
    var time = new Date();
    time.setUTCHours(time.getUTCHours()+9);
    var hour = time.getUTCHours().toString();
    var minute = time.getUTCMinutes().toString();
    if (hour.length<2) hour='0'+hour;
    if (minute.length<2) minute='0'+minute;
    
    return hour+':'+minute;
};

/**************************************************************************
 * AJAX SETUP
 */
$(function() {
    $.ajaxSetup({
		dataType: 'json',
        beforeSend: function(pJqXHR, pSettings) {
            if (pSettings.validate) {
                if (!pSettings.validate()) {
                    return false;
                }
            }
            fnLoadding();
        },
        error: function(pJqXHR, pTextStatus, pErrorThrown) {
            fnLoadding('hide');
            if (pJqXHR.status === 200) {
                alert(pTextStatus);
                if (pTextStatus === 'parsererror') {
                    fnAlert(fnGetMessage(pJqXHR.responseText), 'error');
                    console.error(pJqXHR);
                }
            } else if (pJqXHR.status === 401) {
            } else if (pJqXHR.status === 403) {
                fnAlert(fnGetMessage(pJqXHR.responseJSON.message), 'error');
            } else {
                toastrError(pJqXHR);
            }
        },
        complete: function(pJqXHR, pTextStatus) {
            fnLoadding('hide');
        },
        statusCode: {
            401: function() {
                alert('로그인 후 이용가능합니다.');
                location.href = '/';
            }
        }
    });
});
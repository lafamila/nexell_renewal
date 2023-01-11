$(function() {
    /**************************************************************************
     * DATATABLE INIT
     */
    $.extend(true, $.fn.dataTable.defaults, {
        // dom: 'r<"row"<"col-xs-6"i><"col-xs-6 text-right"l>>tp',
        // dom: "t<'dt-toolbar-footer'<'col-sm-6 col-xs-12 hidden-xs'i><'col-xs-12 col-sm-6'p>>",
        // dom: "Bt<'dt-toolbar-footer'<'col-sm-6 col-xs-12 hidden-xs'i><'col-xs-12 col-sm-6'p>>",
        dom: "<'hidden'Bl>t<'dt-toolbar-footer'<'col-sm-6 col-xs-12 hidden-xs'i><'col-xs-12 col-sm-6'p>>",
        info: true,
        lengthChange: true,
        lengthMenu: [
            [10, 20, 30, 50, -1], // value
            ['10건씩', '20건씩', '30건씩', '50건씩', 'ALL'] // label
        ],
        paging: true,
        pageLength: 10,
        autoWidth: false,
        orderMulti: false,
        processing: false,
        // stateSave: true,
        columnDefs: [
            { orderable: false, targets: [0] }
        ],
        language: {
            info: '<i class="fa fa-chevron-right"></i> 전체 <span>_MAX_</span>건의 검색결과 중 <span>_START_～_END_</span>',
            infoEmpty: '<i class="fa fa-chevron-right"></i> 전체 <span>0</span>건의 검색결과 중 <span>0～0</span>',
            lengthMenu: '_MENU_',
            infoFiltered: '',
            loadingRecords: '로딩중입니다...',
            processing: '조회중입니다...',
            emptyTable: '<b>조회된 내용이 없습니다.</b>',
            paginate: {
                previous: '이전',
                next: '다음'
            },
        },
        buttons: [
            'excelHtml5',
		],
    });

    /**************************************************************************
     * 달력 플러그인 초기화
     */
    $.datepicker.setDefaults({
        dateFormat: 'yy-mm-dd',
        // format: 'yyyy-mm-dd',
        prevText: '<i class="fa fa-chevron-left"></i>',
        nextText: '<i class="fa fa-chevron-right"></i>',
        monthNames: ['1월', '2월', '3월', '4월', '5월', '6월', '7월', '8월', '9월', '10월', '11월', '12월'],
        monthNamesShort: ['1월', '2월', '3월', '4월', '5월', '6월', '7월', '8월', '9월', '10월', '11월', '12월'],
        dayNames: ['일요일', '월요일', '화요일', '수요일', '목요일', '금요일', '토요일'],
        dayNamesShort: ['일', '월', '화', '수', '목', '금', '토'],
        dayNamesMin: ['일', '월', '화', '수', '목', '금', '토'],
        showMonthAfterYear: true,
        yearSuffix: ' ',
        changeYear: true, //콤보박스에서 년 선택 가능
		changeMonth: true, //콤보박스에서 월 선택 가능
		showButtonPanel: true, // 캘린더 하단에 버튼 패널을 표시한다. 
    });

    /**************************************************************************
     * SELECT2 컴포넌트 포커스 이벤트 처리
     */
    $('.select2-selection--single').on('focus', function(event) {
        var select2_open = $(this).parent().parent().siblings('select');
        select2_open.select2('open');
    });

    /**************************************************************************
     * TOASTR INIT
     */
    toastr = null;
    try {
        toastr.options = {
            "closeButton": true,
            "debug": false,
            "progressBar": true,
            "positionClass": "toast-bottom-right",
            "onclick": null,
            "showDuration": "300",
            "hideDuration": "1000",
            "timeOut": "3000",
            "extendedTimeOut": "1000",
            "showEasing": "swing",
            "hideEasing": "linear",
            "showMethod": "fadeIn",
            "hideMethod": "fadeOut"
        };
    } catch(e) { }

    /**************************************************************************
     * TOOLTIPS INIT
     */
    $(document).find('.tooltips').tooltip();

    /**************************************************************************
     * POPOVERS INIT
     */
    $(document).find('.popovers').popover();

    /**************************************************************************
     * 
     */
    $('input').attr('autocomplete','off');
});
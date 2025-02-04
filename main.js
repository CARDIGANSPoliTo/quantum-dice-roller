"use strict";

function dice_initialize(container) {
    $t.remove($t.id('loading_text'));

    var canvas = $t.id('canvas');
    canvas.style.width = window.innerWidth - 1 + 'px';
    canvas.style.height = window.innerHeight - 1 + 'px';
    var label = $t.id('label');
    var set = $t.id('set');
    var selector_div = $t.id('selector_div');
    var info_div = $t.id('info_div');
    var waiting_div = $t.id('waiting_div');
    on_set_change();

    $t.dice.use_true_random = false;

    function on_set_change(ev) { set.style.width = set.value.length + 3 + 'ex'; }
    $t.bind(set, 'keyup', on_set_change);
    $t.bind(set, 'mousedown', function(ev) { ev.stopPropagation(); });
    $t.bind(set, 'mouseup', function(ev) { ev.stopPropagation(); });
    $t.bind(set, 'focus', function(ev) { $t.set(container, { class: '' }); });
    $t.bind(set, 'blur', function(ev) { $t.set(container, { class: 'noselect' }); });

    $t.bind($t.id('clear'), ['mouseup', 'touchend'], function(ev) {
        ev.stopPropagation();
        set.value = '0';
        on_set_change();
    });

    var params = $t.get_url_params();

    if (params.chromakey) {
        $t.dice.desk_color = 0x00ff00;
        info_div.style.display = 'none';
        $t.id('control_panel').style.display = 'none';
    }
    if (params.shadows == 0) {
        $t.dice.use_shadows = false;
    }
    switch (params.color) {
        case 'white':
            $t.dice.dice_color = '#808080';
            $t.dice.label_color = '#202020';
            break;
        case 'red':
            $t.dice.dice_color = '#d10e00';
            $t.dice.label_color = '#202020';
            break;
        case 'blue':
            $t.dice.dice_color = '#1883db';
            $t.dice.label_color = '#202020';
            break;
        case 'green':
            $t.dice.dice_color = '#008a17';
            $t.dice.label_color = '#202020';
            break;
        case 'orange':
            $t.dice.dice_color = '#fc7b03';
            $t.dice.label_color = '#202020';
            break;
        case 'purple':
            $t.dice.dice_color = '#7d0099';
            $t.dice.label_color = '#aaaaaa';
            break;
        case 'brown':
            $t.dice.dice_color = '#593304';
            $t.dice.label_color = '#aaaaaa';
            break;
        default:
            break;
    }

    var box = new $t.dice.dice_box(canvas, { w: 500, h: 300 });
    box.animate_selector = false;

    $t.bind(window, 'resize', function() {
        canvas.style.width = window.innerWidth - 1 + 'px';
        canvas.style.height = window.innerHeight - 1 + 'px';
        box.reinit(canvas, { w: 500, h: 300 });
    });

    function show_selector() {
        info_div.style.display = 'none';
        selector_div.style.display = 'inline-block';
        box.draw_selector();
    }

    function before_roll(vectors, notation, callback) {
        info_div.style.display = 'none';
        selector_div.style.display = 'none';
        canvas.style.display = 'none';
        waiting_div.style.display = 'block';
        
        // console.log(notation.set[0])
        
        var res;
        fetch('/dice/f', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                data: notation.set
            })
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data =>  {
            res = data;
            // console.log(res)
        })
        .then(() =>  {
            // console.log(res)
            // console.log(res.number)
            // do here rpc call or whatever to get your own result of throw.
            // then callback with array of your result, example:
            waiting_div.style.display = 'none';
            canvas.style.display = 'inline-block';
            callback(res.number);
        })
        .catch(error => {
            console.error('There was a problem with the fetch operation:', error);
        });
    }

    function notation_getter() {
        return $t.dice.parse_notation(set.value);
    }

    function after_roll(notation, result) {
        if (params.chromakey || params.noresult) return;
        var res = result.join(' + ');
        if (notation.constant) {
            res += ' (';
            if (notation.constant > 0) res += '+' + notation.constant;
            else res += '-' + Math.abs(notation.constant);
            res += ')';
        }
        if (result.length > 1) res += ' = ' + 
                (result.reduce(function(s, a) { return s + a; }) + notation.constant);
        label.innerHTML = res;
        info_div.style.display = 'inline-block';
    }

    box.bind_mouse(container, notation_getter, before_roll, after_roll);
    box.bind_throw($t.id('throw'), notation_getter, before_roll, after_roll);

    $t.bind(container, ['mouseup', 'touchend'], function(ev) {
        ev.stopPropagation();
        if (selector_div.style.display == 'none') {
            if (!box.rolling) show_selector();
            box.rolling = false;
            return;
        }
        var name = box.search_dice_by_mouse(ev);
        if (name != undefined) {
            var notation = $t.dice.parse_notation(set.value);
            notation.set.push(name);
            set.value = $t.dice.stringify_notation(notation);
            on_set_change();
        }
    });

    if (params.notation) {
        set.value = params.notation;
    }
    if (params.roll) {
        $t.raise_event($t.id('throw'), 'mouseup');
    }
    else {
        show_selector();
    }
}

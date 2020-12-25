var animation_canvas = document.getElementById('animation');
// animation_canvas.width = window.innerWidth;
// animation_canvas.height = window.innerHeight/2;
var height_sim = window.innerHeight - 200;
var scene, camera, renderer, renderer2, renderer3, raycaster;
var lights = [];
var tape_box1_mesh, tape_box2_mesh;
var  index_for_arrow, number_of_letters_to_display, letter_box_side_length, camera_angle, state_to_display, radius;
var canvas_size, arrow_position, middle_letter_position;
const textureLoader = new THREE.TextureLoader();
var enter_call, not_initiated;
var input;
var instructions, example, letters, elements, letter_positions;
var position_lookAt;
const init_camera_pos = new THREE.Vector3(0, 0, 25);
var init_lookAt_pos;
const colors = [0xE199FF, 0xFFFFFF, 0x49F8FF, 0xFFBD00, 0x6AFE8B, 0xFF31A7, 0x54FFFB];
var crystals = [];
var start_moving = false;
var interval = 2000;
var lastTime = 0;

function init()
{
    show_all = true;

    instructions = [];
    index_for_arrow = [];
    example = [];
    letters = [];
    elements = [];
    letter_positions = [];

    number_of_letters_to_display = 15;
    letter_box_side_length = 20;
    camera_angle = 0;
    state_to_display = 0;

    canvas_size = new THREE.Vector2(700, 700);
    arrow_position = new THREE.Vector3(0, -15, 0);
    middle_letter_position = new THREE.Vector3(0, 0, 0);
    position_lookAt = new THREE.Vector3(middle_letter_position.x, middle_letter_position.y, middle_letter_position.z);
    init_lookAt_pos = new THREE.Vector3(middle_letter_position.x, middle_letter_position.y, middle_letter_position.z);

    enter_call = 0;
    not_initiated = true;

    scene = new THREE.Scene();
    camera = new THREE.PerspectiveCamera(145,window.innerWidth/height_sim,0.1,1000);
    camera.position.set(init_camera_pos.x,init_camera_pos.y,init_camera_pos.z);
    camera.lookAt(position_lookAt);
    renderer = new THREE.WebGLRenderer({ alpha: true });
    renderer.setPixelRatio( window.devicePixelRatio );
    renderer.domElement.style.position = 'absolute';
    renderer.domElement.style.top = 0;
    renderer.domElement.style.zIndex = '1';
    renderer.setSize(window.innerWidth, height_sim);

    radius = camera.position.z - position_lookAt.z;

    renderer2 = new THREE.CSS3DRenderer();
    renderer2.setSize(window.innerWidth, height_sim);
    renderer2.domElement.style.position = 'absolute';
    renderer2.domElement.style.top = 0;
    renderer2.domElement.style.zIndex = '2';
    animation_canvas.appendChild(renderer2.domElement);
    animation_canvas.appendChild(renderer.domElement);

    renderer3 = new THREE.WebGLRenderer();
    renderer.setPixelRatio( window.devicePixelRatio );
    renderer.domElement.style.position = 'absolute';
    renderer.domElement.style.top = 0;
    renderer.domElement.style.zIndex = '3';
    renderer.setSize(window.innerWidth, height_sim);

    raycaster = new THREE.Raycaster();

    var material = glossy_material(colors[0]);


    for(var i=0; i<5; i++)
    {
        var l = new THREE.PointLight(colors[i%colors.length], 2, 1000);
        l.position.set((Math.random() - 0.5) * 1000,Math.random()*10,Math.random()*100);
        l.rotation.set(Math.random(),Math.random(),Math.random());
        lights.push(l);
        scene.add(l);
    }

    camera.updateProjectMatrix;

    eventListeners();
}

function glossy_material(color)
{
    const clearcoatNormaMap = textureLoader.load( document.getElementById('scratched').textContent );
    var material = new THREE.MeshPhysicalMaterial( {
            map: clearcoatNormaMap,
            color: color,
            metalness: 0.8,
            roughness: 0.5,
            opacity: 0.8,
            transparent: false,
            envMapIntensity: 5,
            premultipliedAlpha: true
        } );

    return material;
}

function reset_all()
{
    instructions = [];
    index_for_arrow = [];
    state_to_display = 0;
    example = [];
    letter_positions = [];
    letters = [];
    elements = [];
    var elems = document.getElementsByClassName('element');
    var i = elems.length;
    while(i > 0)
    {
        document.removeChild(elems[i-1]);
        i--;
    }

    camera.updateProjectMatrix;
}

function eventListeners()
{
    window.addEventListener('resize',() => {
        renderer.setSize(window.innerWidth, height_sim);
        renderer2.setSize(window.innerWidth, height_sim);
        camera.aspect = window.innerWidth/height_sim;
        camera.updateProjectMatrix;
    });


    window.addEventListener('keydown', function(event){
        switch(event.code)
        {
            case "Space":
                break;
            case "Enter":
                if(not_initiated)
                {
                    init_letters();
                    start_moving = true;
                }
                if(!not_initiated)
                {
                    prepare_arrow();
                    setInterval(function(){go();}, 2000);
                }
                break;
            default:
                break;

        }

        camera.updateProjectMatrix;

    });
}

function go()
{
    if(enter_call%2 == 0)
    {
        next_machine_state();
        enter_call++;
    }
    else
    {
        update_letter();
        enter_call++;
    }
}

function render()
{
    renderer.render(scene,camera);
    renderer2.render(scene,camera);
    renderer3.render(scene, camera);
}

function is_numeric_char(c) { return /\d/.test(c); }

function init_letters()
{
    var additional_empty_signs = (number_of_letters_to_display - 1)/2 + 15;
    var empty_signs = []
    for(var i=0; i<additional_empty_signs; i++)
    {
        empty_signs.push('#');
    }

    var result = document.getElementById("lines").textContent;

    var lines = result.split('\n');
    for(var i = 0; i < lines.length; i++)
    {
        var line = lines[i];
        if(line[0] == 'E')
        {
            for(var j = 2; j<line.length; j++)
            {
                var letter = line[j];
                if(letter != '[' && letter != '\'' && letter != ',' && letter != ' ' && letter != ']')
                {
                    example.push(letter);
                }
            }
        }
        else if(line[0] == '[')
        {
            //czyt instrukcje
            var instr = [];
            instr = instr.concat(empty_signs);
            for(var j = 1; j<line.length; j++)
            {
                var letter = line[j];
                if(letter != '[' && letter != '\'' && letter != ',' && letter != ' ' && letter != ']')
                {
                    instr.push(letter);
                }
            }
            instr = instr.concat(empty_signs);
            instructions.push(instr);
        }
        else if(line[0] == '#')
        {
            //czyt index_for_arrow
            for(var j = 1; j<line.length; j++)
            {
                var letter = line[j];
                if(is_numeric_char(letter))
                {
                    index_for_arrow.push(additional_empty_signs + parseInt(letter));
                }
            }
        }
    }

    not_initiated = false;
    document.getElementById('enter-info').style.visibility = 'hidden';
}

function prepare_arrow()
{
    if(not_initiated) return;
    const metal_map = textureLoader.load( document.getElementById('metal').textContent );
    const clearcoatNormaMap = textureLoader.load( document.getElementById('scratched').textContent );
    material = new THREE.MeshPhysicalMaterial( {
                        clearcoat: 0.5,
                        metalness: 1.0,
                        color: 0xA40FA3,
                        normalMap: metal_map,
                        normalScale: new THREE.Vector2( 0.15, 0.15 ),
                        clearcoatNormalMap: clearcoatNormaMap,
                        clearcoatNormalScale: new THREE.Vector2( 2.0, - 2.0 )
                    } );
    const geometry = new THREE.ConeGeometry( 5, 20, 32 );
    const cone = new THREE.Mesh( geometry, material );
    cone.position.set(arrow_position.x,arrow_position.y,arrow_position.z);
    cone.scale.set(0.5, 0.5, 0.5);
    scene.add( cone );
}

function prepare_letter(curr_letter, position_vector, is_visible, at_beggining = false)
{
    var element = document.createElement( 'div' );
    element.className = 'element';
    element.style.width = letter_box_side_length + 'px';
    element.style.height = letter_box_side_length + 'px';
    element.style.backgroundColor = 'rgba(255, 127, 244,' + ( Math.random() * 0.5 + 0.25 ) + ')';
    element.style.visibility = is_visible;

    var letter = document.createElement( 'div' );
    letter.className = 'letter';
    letter.style.fontSize = '15px';
    letter.textContent = curr_letter;
    element.appendChild( letter );
    element.style.visibility = is_visible;

    var objectCSS = new THREE.CSS3DObject( element );
    objectCSS.position.x = position_vector.x;
    objectCSS.position.y = position_vector.y;
    objectCSS.position.z = position_vector.z;

    if(at_beggining)
    {
        insert_in_array(letters, 0, objectCSS);
        insert_in_array(elements, 0, element);
    }
    else
    {
        letters.push(objectCSS);
        elements.push(element);
    }

}

function update_letter()
{
    if(not_initiated) return;
    if(state_to_display && state_to_display<instructions.length)
    {
        var index_of_middle = index_for_arrow[state_to_display];
        var new_letter = instructions[state_to_display][index_of_middle];
        letters[index_of_middle].element.getElementsByClassName('letter')[0].textContent = new_letter;
    }
    state_to_display += 1;
}

function update_visibility()
{
    if(state_to_display >= instructions.length)
    {
        return;
    }
    var visibility;
    var letters_on_each_side = (number_of_letters_to_display + 1) / 2;
    var index_of_middle = index_for_arrow[state_to_display];

    for(var i=0; i<letters.length; i++)
    {
        visibility = 'hidden';
        if(index_of_middle + letters_on_each_side >= i && index_of_middle - letters_on_each_side <= i) visibility = 'visible';
        elements[i].style.visibility = visibility;
    }
}

function insert_in_array(arr, index, item )
{
    arr.splice( index, 0, item );
};

function move_tape(to_right)
{
    TWEEN.removeAll();
    letters_on_each_side = (number_of_letters_to_display - 1)/2;

    if(to_right)
    {
        for(var i = letters.length - 1; i >= 1; i--)
        {
            new TWEEN.Tween( letters[i].position )
                    .to( { x: letters[i-1].position.x, y: letters[i-1].y, z: letters[i-1].z}, 2000 )
                    .easing( TWEEN.Easing.Exponential.InOut )
                    .start();
        }

        new TWEEN.Tween( letters[0].position )
                    .to( { x: letters[0].position.x - letter_box_side_length - 10, y: letters[0].y, z: letters[0].z}, 2000 )
                    .easing( TWEEN.Easing.Exponential.InOut )
                    .start();

    }
    else
    {
        for(var i = 0; i < letters.length-1; i++)
        {
            new TWEEN.Tween( letters[i].position )
                    .to( { x: letters[i+1].position.x, y: letters[i+1].y, z: letters[i+1].z}, 2000 )
                    .easing( TWEEN.Easing.Exponential.InOut )
                    .start();
        }
        new TWEEN.Tween( letters[letters.length-1].position )
                    .to( { x: letters[letters.length-1].position.x + letter_box_side_length + 10,
                    y: letters[letters.length-1].y, z: letters[letters.length-1].z}, 2000 )
                    .easing( TWEEN.Easing.Exponential.InOut )
                    .start();

    }


    new TWEEN.Tween( this )
    .to( {}, 2000 )
    .onUpdate( render )
//    .onComplete(update_letter)
    .start();

}

function pretty_string(arr)
{
    var str = "";
    var i= 0;
    while(arr[i] == '#')
    {
        i++;
    }
    while(i < arr.length && arr[i] != '#')
    {
        str += arr[i];
        i++;
    }

    return str;
}

function next_machine_state()
{
    if(not_initiated) return;
    if(state_to_display == 0)
    {
        var h2 = document.createElement('h2');
        // h2.textContent = "Example given: " + example.toString().replace(",", " ");
        h2.textContent = "Example given: " + pretty_string(example);
        document.body.appendChild(h2);
    }
    if(state_to_display == instructions.length)
    {
        var h1 = document.createElement('h1');
        h1.textContent = "Finished";
        document.body.appendChild(h1);

        var h3 = document.createElement('h3');
        var result = document.getElementById("last_value").textContent;

        //depending on machine being decisive or not
        if(result == 'None')
        {
            h3.textContent = "Final state: " + pretty_string(instructions[instructions.length - 1]);
        }
        else
        {
            h3.textContent = "Final state: " + result;
        }
        document.body.appendChild(h3);
        return;
    }

    if(state_to_display > instructions.length)
    {
        return;
    }

    var letters_on_each_side = (number_of_letters_to_display - 1)/2;
    var index_of_middle = index_for_arrow[state_to_display];
    var start_vector = new THREE.Vector3(middle_letter_position.x - (letter_box_side_length + 10)*letters_on_each_side,
                         middle_letter_position.y, middle_letter_position.z);


    if(letters.length == 0)
    {
        //pozycja tego, na ktory ma wskazywac strzalka (middle) - ilość literek przed nim w instrukcji * (dlugosc boku + odstep od kolejnej literki)
        var start_position_x = middle_letter_position.x - index_of_middle * (letter_box_side_length + 10);
        for(var j=0; j<instructions[0].length; j++)
        {
            var temp = new THREE.Vector3(start_position_x + j*(letter_box_side_length + 10), middle_letter_position.y, middle_letter_position.z);
            letter_positions.push(temp);
            var is_visible = 'hidden';
            if ( index_of_middle + letters_on_each_side >= j && index_of_middle - letters_on_each_side <= j) is_visible = 'visible';
            prepare_letter(instructions[0][j], temp, is_visible);
            scene.add(letters[j]);
        }

    }
    else
    {
        if(index_of_middle < index_for_arrow[state_to_display - 1])
        {
            move_tape(false);
        }
        else
        {
            move_tape(true);
        }
    }

//    state_to_display += 1;
}

function in_delay()
{
//    next_machine_state();
    TWEEN.update();
//    update_letter();
    update_visibility();
}

function animate() {
//    if ( (Date.now() - lastTime) < interval) {
//        return;
//    }
//    lastTime = Date.now();
    requestAnimationFrame( animate );
//    prepare_arrow();
    in_delay();
    render();
}


init();
animate();


database = [
    {id: 100, name: "침대", width: 2, height: 3, sprite: "/static/sprites/100_bed.png"},
    {id: 101, name: "책상", width: 2, height: 1, sprite: "/static/sprites/101_desk.png"},
    {id: 102, name: "의자", width: 1, height: 1, sprite: "/static/sprites/102_chair.png"},
    {id: 103, name: "소파", width: 3, height: 1, sprite: "/static/sprites/103_sofa.png"},
    {id: 104, name: "화분", width: 1, height: 1, sprite: "/static/sprites/104_pot.png"},
    {id: 105, name: "스탠딩조명", width: 1, height: 1, sprite: "/static/sprites/105_light.png"},
    {id: 106, name: "탁자", width: 2, height: 1, sprite: "/static/sprites/106_table.png"},
    {id: 107, name: "곰인형", width: 1, height: 1, sprite: "/static/sprites/107_doll.png"},
    {id: 108, name: "변기", width: 1, height: 1, sprite: "/static/sprites/108_toilet.png"},
    {id: 109, name: "세면대", width: 1, height: 1, sprite: "/static/sprites/109_sink.png"},
    {id: 110, name: "쓰레기통", width: 1, height: 1, sprite: "/static/sprites/110_bin.png"},
]

let state = {
    x: 0,
    y: 0,
    rotation: 0,
    object_id: 100,
    new_item: null,
}
let items = [
    {object_id: 100, instance_id: 100, x: 0, y: 0, r: 0}
]

function redraw(objects)
{
    objects = [...items, state.new_item];
    document.getElementById("rotation").innerText = state.rotation;
    const imgs = [...document.querySelectorAll(".grid-item img")];
    for (let img of imgs) {
        img.src = "";
        img.className = "";
    }
    for (let object of objects) {
        if (object == null || object.object_id < 100) continue;
        const meta = database.filter(x => x.id == object.object_id)[0];
        let {width, height} = meta;
        if (object.r % 2 == 1) {
            const temp = width;
            width = height;
            height = temp;
        }
        console.log(object)
        for (let x = 0; x < width; x++) {
            for (let y = 0; y < height; y++) {
                const img = document.querySelector(`#cell-${object.x + x}-${object.y + y} img`)
                if (img == null) {
                    document.body.style="background-color: #aaaaaa;";
                    return;
                }
                img.src = meta.sprite;
                img.className = `rotate-${object.r * 90}`;
            }
        }
    }
    document.body.style="background-color: white;";
}

document.addEventListener("keydown", (x) =>{
    const key = x.key.toLowerCase();
    if (key == "`") set_item(100, state.x, state.y, state.rotation);
    if (key == "1") set_item(101, state.x, state.y, state.rotation);
    if (key == "2") set_item(102, state.x, state.y, state.rotation);
    if (key == "3") set_item(103, state.x, state.y, state.rotation);
    if (key == "4") set_item(104, state.x, state.y, state.rotation);
    if (key == "5") set_item(105, state.x, state.y, state.rotation);
    if (key == "6") set_item(106, state.x, state.y, state.rotation);
    if (key == "7") set_item(107, state.x, state.y, state.rotation);
    if (key == "8") set_item(108, state.x, state.y, state.rotation);
    if (key == "9") set_item(109, state.x, state.y, state.rotation);
    if (key == "0") set_item(110, state.x, state.y, state.rotation);
    if (key == "r" && state.new_item != null) {
        const new_rotation = (state.rotation + 1) % 4;
        set_item(state.id, state.x, state.y, new_rotation);
    }
})

function set_item(id, x, y, rotation) {
    state.id = id;
    state.x = x;
    state.y = y;
    state.rotation = rotation;
    state.new_item = {object_id: id, instance_id: 999, x: x, y: y, r: rotation }
    redraw();
}
document.querySelectorAll(".grid-item").forEach(x => x.addEventListener("click", (e) => {
    const cell = e.target.tagName == "IMG" ? e.target.parentElement.id : e.target.id;
    const [_, x, y] = cell.split("-");
    set_item(state.object_id, +x, +y, state.rotation);
}))

redraw()

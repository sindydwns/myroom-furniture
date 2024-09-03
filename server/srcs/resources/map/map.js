database = [
    { id: 1, name: "방", width: 0, height: 0, sprite: "" },
    { id: 2, name: "벽", width: 0, height: 0, sprite: "" },
    { id: 3, name: "창문", width: 0, height: 0, sprite: "" },
    { id: 100, name: "침대", width: 2, height: 3, sprite: "/static/sprites/100_bed.png" },
    { id: 101, name: "책상", width: 2, height: 1, sprite: "/static/sprites/101_desk.png" },
    { id: 102, name: "의자", width: 1, height: 1, sprite: "/static/sprites/102_chair.png" },
    { id: 103, name: "소파", width: 3, height: 1, sprite: "/static/sprites/103_sofa.png" },
    { id: 104, name: "화분", width: 1, height: 1, sprite: "/static/sprites/104_pot.png" },
    { id: 105, name: "스탠딩조명", width: 1, height: 1, sprite: "/static/sprites/105_light.png" },
    { id: 106, name: "탁자", width: 2, height: 1, sprite: "/static/sprites/106_table.png" },
    { id: 107, name: "곰인형", width: 1, height: 1, sprite: "/static/sprites/107_doll.png" },
    { id: 108, name: "변기", width: 1, height: 1, sprite: "/static/sprites/108_toilet.png" },
    { id: 109, name: "세면대", width: 1, height: 1, sprite: "/static/sprites/109_sink.png" },
    { id: 110, name: "쓰레기통", width: 1, height: 1, sprite: "/static/sprites/110_bin.png" },
]

let state = {
    x: 0,
    y: 0,
    rotation: 0,
    object_id: 100,
    draw: false,
    new_item: null,
}
let items = [
    // { object_id: 100, instance_id: 100, x: 0, y: 0, r: 0 }
]
let _env_file;
let _cmd;

function redraw() {
    const objects = [...items];
    if (state.draw) objects.push(state.new_item);
    document.getElementById("rotation").innerText = `${state.rotation * 90}`;
    const meta = getMeta(state.object_id);
    document.getElementById("image").src = meta.sprite;
    const imgs = [...document.querySelectorAll(".grid-item img")];
    for (let img of imgs) {
        img.src = "";
        img.className = "";
    }
    const texts = [...document.querySelectorAll(".grid-item .instance")]
    for (let text of texts) {
        text.innerHTML = ""
    }
    for (let object of objects) {
        if (object == null || object.object_id < 100) continue;
        const meta = getMeta(object.object_id);
        let { width, height } = meta;
        if (object.r % 2 == 1) {
            const temp = width;
            width = height;
            height = temp;
        }
        for (let x = 0; x < width; x++) {
            for (let y = 0; y < height; y++) {
                const img = document.querySelector(`#cell-${object.x + x}-${object.y + y} img`)
                const instanceText = document.querySelector(`#cell-${object.x + x}-${object.y + y} .instance`)
                if (img == null) {
                    document.body.style = "background-color: #aaaaaa;";
                    return;
                }
                img.src = meta.sprite;
                img.className = `rotate-${(object.r % 4) * 90}`;
                instanceText.innerText = object.instance_id == 999 ? "" : object.instance_id;
            }
        }
    }
    document.body.style = "background-color: white;";
}

document.addEventListener("keydown", (x) => {
    const key = x.key.toLowerCase();
    if (key == "`") set_item(100, state.x, state.y, state.rotation, true);
    if (key == "1") set_item(101, state.x, state.y, state.rotation, true);
    if (key == "2") set_item(102, state.x, state.y, state.rotation, true);
    if (key == "3") set_item(103, state.x, state.y, state.rotation, true);
    if (key == "4") set_item(104, state.x, state.y, state.rotation, true);
    if (key == "5") set_item(105, state.x, state.y, state.rotation, true);
    if (key == "6") set_item(106, state.x, state.y, state.rotation, true);
    if (key == "7") set_item(107, state.x, state.y, state.rotation, true);
    if (key == "8") set_item(108, state.x, state.y, state.rotation, true);
    if (key == "9") set_item(109, state.x, state.y, state.rotation, true);
    if (key == "0") set_item(110, state.x, state.y, state.rotation, true);
    if (key == "r" && state.new_item != null) {
        const new_rotation = (state.rotation + 1) % 4;
        set_item(state.object_id, state.x, state.y, new_rotation, true);
    }
    if (key == " ") {
        submit();
    }
})

function set_item(id, x, y, rotation, draw = false) {
    state.object_id = id;
    state.x = x;
    state.y = y;
    console.trace(rotation);
    state.rotation = rotation;
    state.draw = draw;
    state.new_item = { object_id: id, instance_id: 999, x: x, y: y, r: rotation }
    redraw();
}
document.querySelectorAll(".grid-item").forEach(x => x.addEventListener("click", (e) => {
    const cell = e.target.className != "grid-item" ? e.target.parentElement.id : e.target.id;
    const [_, x, y] = cell.split("-");
    set_item(state.object_id, +x, +y, state.rotation, true);
}))

function getMeta(id) {
    return database.filter(x => x.id == id)[0];
}

function getItem(instance_id) {
    return items.filter(x => x.instance_id == instance_id)[0];
}

async function checkout() {
    try {
        const rawData = await fetch("/sample")
        if (rawData.status != 200) throw "x"
        const jsonData = await rawData.json();
        const { cmd, cmd_str, env, env_name } = jsonData;
        console.log(jsonData)
        items = env;
        _env_file = env_name
        _cmd = cmd_str;

        const meta = getMeta(jsonData.cmd.object_id);
        let pre_rotation = jsonData.cmd.rotation;
        let pre_x = 0;
        let pre_y = 0;
        if (jsonData.cmd.mode == "E") {
            const instance = getItem(jsonData.cmd.instance_id);
            pre_rotation += instance.r;
            pre_x += instance.x;
            pre_y += instance.y;
        }
        const { mode, object_id, instance_id, rotation, locations } = cmd;
        const strMode = mode == "A" ? "추가" : "수정";
        const strObjectName = getMeta(object_id).name;
        const strInstanceId = mode == "A" ? "" : `(${instance_id})`
        const strRotation = rotation > 0 ? `${rotation * 90}도 회전` : ""
        const strLocations = locations.map(x => locationToStr(x))
        document.getElementById("cmd").innerText = `${strObjectName}${strInstanceId} ${strMode}. ${strRotation} ${strLocations}`;

        set_item(meta.id, pre_x, pre_y, pre_rotation)
    } catch (e) {
        window.location.reload()
    }
}

function locationToStr(x) {
    let strLocation = ""
    if (x[0] == "ne") strLocation = "근처에"
    if (x[0] == "fa") strLocation = "멀리에"
    if (x[0] == "le") strLocation = "왼쪽에"
    if (x[0] == "ri") strLocation = "오른쪽에"
    if (x[0] == "on") strLocation = "위에"
    if (x[0] == "un") strLocation = "아래에"
    if (x[0] == "in") strLocation = "안에"
    if (x[0] == "fr") strLocation = "앞에"
    if (x[0] == "ba") strLocation = "뒤에"
    if (x[0] == "ce") strLocation = "중앙에"
    return `${getMeta(getItem(x[1]).object_id).name}(${x[1]}) ${strLocation}`
}

let doubleCheck = false;
async function submit() {
    if (state.draw == false) return;
    if (doubleCheck) return;
    doubleCheck = true;
    const data = {
        res: {
            object_id: state.object_id,
            instance_id: +(_cmd.split(" ")[1]),
            x: state.new_item.x,
            y: state.new_item.y,
            r: state.rotation
        },
        cmd: _cmd,
        env_file: _env_file,
    }
    try {
        console.log(JSON.stringify(data));
        const res = await fetch("/trainset", {
            method: "post",
            headers: {
                "Accept": "application/json",
                "Content-Type": "application/json",
            },
            body: JSON.stringify(data)
        });
        if (res.status != 200) throw "x"
    } catch (e) {
        console.log(e);
        alert("전송 실패");
    }
    window.location.reload()
}

checkout()

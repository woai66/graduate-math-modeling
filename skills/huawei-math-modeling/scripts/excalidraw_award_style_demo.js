/**
 * 用原生 Excalidraw 元素重绘用户给出的园林论文路线图风格样例。
 * create 新建源图；inspect 读取画布；edit 执行一次文字及布局修改；
 * export 使用插件从已保存源图导出。所有写入仅限本次独立测试件。
 * 调用方提供 ea、app、mode；不调用任何 AI 或远程绘图服务。
 */
const BASE = '20_学习/研究生数模竞赛/skills/huawei-math-modeling/assets';
const STEM = 'excalidraw-award-style-demo';
const PATH = `${BASE}/${STEM}.excalidraw.md`;
const C = {
    ink: '#20252B', line: '#424D67', green: '#578B45', blue: '#5264A5',
    red: '#B86169', cyan: '#397C86', gold: '#B88D35',
    blueFill: '#F0F3FC', redFill: '#FFF1F0', cyanFill: '#EEF8F6',
};
/**
 * 论文插图配色：NPG（Nature Publishing Group）科研期刊系列的低饱和版本。
 * 色值取自科研绘图常用的 ggsci NPG 方案，去掉高饱和渐变和荧光感，
 * 结构蓝、数据青、青绿、砖红四色分工明确，黑白打印时仍能靠灰度区分。
 * 深色只用于描边和标题，浅色只用于分区底，正文保持近黑。
 */
const NATURE = {
    ink: '#1A1A1A',
    structure: '#3C5488',
    aux: '#8491B4',
    data: '#4DBBD5',
    q1: '#3C5488',
    q2: '#B5534A',
    q3: '#00A087',
    summary: '#B09C85',
    q1Fill: '#EDF1F7',
    q2Fill: '#FBEDEA',
    q3Fill: '#E7F4F1',
    dataFill: '#EAF6FA',
    summaryFill: '#FAF6F0',
    white: '#FFFFFF',
};
const NATURE_TINT = new Set(['raw-data', 'q1-variety', 'q1-interest', 'q2-open', 'q2-close',
    'q2-elements', 'q2-rhythm', 'geometry', 'q1-panel', 'q2-panel', 'q3-panel']);
const NATURE_DATA_ROLES = new Set(['preprocess', 'preprocess-arrow', 'normalization', 'raw-data',
    'coordinate', 'distance', 'geometry', 'curve', 'centerline', 'obstacle', 'passable']);
const NATURE_EXPLICIT = {
    'key-metrics': 'q1', 'plan-compare': 'q1', 'q1-model-down': 'q1',
    'cluster-change': 'q2', 'change-open': 'q2', 'change-close': 'q2',
    'space-perception': 'q2', 'elements-evaluate': 'q2', 'rhythm-evaluate': 'q2',
    'perception-ranking': 'q2', 'q2-to-validation': 'q2', 'validation-feedback': 'q2',
    'quantify-common': 'q3', 'common-validation': 'q3', 'validation-description': 'q3',
    'q1-to-validation': 'aux', 'questions': 'structure',
};
const NATURE_THEME = {
    q1: {stroke: NATURE.q1, fill: NATURE.q1Fill},
    q2: {stroke: NATURE.q2, fill: NATURE.q2Fill},
    q3: {stroke: NATURE.q3, fill: NATURE.q3Fill},
    data: {stroke: NATURE.data, fill: NATURE.dataFill},
    summary: {stroke: NATURE.summary, fill: NATURE.summaryFill},
    structure: {stroke: NATURE.structure, fill: NATURE.white},
    aux: {stroke: NATURE.aux, fill: NATURE.white},
};
const ids = {};
const roles = {};

/** 设置新元素样式；每次重置虚实线和填充，防止样式泄漏。 */
function style(options = {}) {
    Object.assign(ea.style, {
        strokeColor: C.line, backgroundColor: 'transparent', fillStyle: 'solid',
        strokeWidth: 1.8, strokeStyle: 'solid', roughness: 0, roundness: null,
        fontFamily: 2, fontSize: 28, textAlign: 'center', verticalAlign: 'middle',
        startArrowHead: null, endArrowHead: 'triangle', ...options,
    });
}

/** 为原生元素附加语义角色，保留插件的其他 customData。 */
function tag(id, role) {
    ea.addAppendUpdateCustomData(id, {paperFlowRole: role});
    roles[role] = id;
    return id;
}

/** 测量后居中放置文字；背景与文字分别保持可编辑。 */
function text(role, x, y, w, h, value, fontSize = 28, color = C.ink) {
    style({fontSize, strokeColor: color});
    const size = ea.measureText(value);
    if (size.width > w - 6 || size.height > h - 2) {
        throw new Error(`文字超出预留区域 ${role}: ${size.width} x ${size.height} / ${w} x ${h}`);
    }
    return tag(ea.addText(x + (w - size.width) / 2, y + (h - size.height) / 2, value), role);
}

/** 区域背景不绑定整块文字；避免移动单个节点时破坏区域。 */
function region(role, x, y, w, h, color, fill = 'transparent', dashed = false) {
    style({strokeColor: color, backgroundColor: fill, strokeWidth: 2.1,
        strokeStyle: dashed ? 'dashed' : 'solid'});
    return tag(ea.addRect(x, y, w, h), role);
}

/** 图内矩形节点，文字使用原生 containerId 双向绑定。 */
function box(role, x, y, w, h, value, options = {}) {
    const {color = C.line, fill = '#FFFFFF', size = 28} = options;
    style({strokeColor: color, backgroundColor: fill});
    const id = tag(ea.addRect(x, y, w, h), role);
    const label = text(`${role}-text`, x, y, w, h, value, size);
    ea.getElement(label).containerId = id;
    ea.getElement(label).verticalAlign = 'middle';
    ea.getElement(label).textAlign = 'center';
    ea.getElement(id).boundElements = [{type: 'text', id: label}];
    ids[role] = id;
    return id;
}

/** 指定折点和两端连接位置；每条箭头仅在末端设箭头。 */
function arrow(role, points, from, to, {color = C.line, start = [.5, 1], end = [.5, 0],
    dashed = false} = {}) {
    style({strokeColor: color, strokeWidth: 1.9, strokeStyle: dashed ? 'dashed' : 'solid'});
    const binding = {};
    if (from) Object.assign(binding, {startObjectId: from, startFixedPoint: start, startBindMode: 'orbit'});
    if (to) Object.assign(binding, {endObjectId: to, endFixedPoint: end, endBindMode: 'orbit'});
    return tag(ea.addArrow(points, {...binding, startArrowHead: null, endArrowHead: 'triangle',
        elbowed: false}), role);
}

/** 空心箭头是可编辑的闭合线条，用于层级转换。 */
function hollow(role, cx, y, length = 68, width = 54, horizontal = false) {
    const h = width / 2;
    const s = width / 7;
    let pts = [[-s, 0], [s, 0], [s, length - h], [h, length - h],
        [0, length], [-h, length - h], [-s, length - h], [-s, 0]];
    pts = pts.map(([x, t]) => horizontal ? [cx + t, y + x] : [cx + x, y + t]);
    style({strokeColor: C.line, backgroundColor: '#FFFFFF', strokeWidth: 1.7});
    return tag(ea.addLine(pts), role);
}

/** 创建视觉内容；布线空隙与模块尺寸按 16 cm 论文版心预留。 */
function build() {
    ea.reset();
    ea.canvas.theme = 'light';
    ea.canvas.viewBackgroundColor = '#FFFFFF';
    region('preprocess', 0, 0, 1080, 224, C.green, '#FFFFFF');
    text('preprocess-title', 320, 13, 440, 47, '数据预处理', 32);
    box('raw-data', 32, 84, 160, 102, '园林数据\n坐标', {color: '#D6E8C8', fill: '#D6E8C8', size: 28});
    text('brace', 207, 84, 48, 103, '{', 86);
    region('normalization', 262, 84, 224, 102, C.green, 'transparent', true);
    box('coordinate', 280, 94, 188, 36, '坐标统一', {size: 24});
    box('distance', 280, 143, 188, 36, '定义距离', {size: 24});
    hollow('preprocess-arrow', 511, 135, 63, 49, true);
    region('geometry', 604, 80, 444, 112, C.line, '#FAFBFD');
    box('curve', 620, 94, 196, 37, '转化连续曲线', {size: 24});
    box('centerline', 836, 94, 196, 37, '建立中心线', {size: 24});
    box('obstacle', 620, 144, 196, 37, '定义障碍面域', {size: 24});
    box('passable', 836, 144, 196, 37, '建立可通行域', {size: 24});

    region('questions', 0, 272, 1080, 772, C.blue, '#FFFFFF', true);
    region('q1-panel', 22, 310, 300, 690, '#8494CE', C.blueFill);
    region('q2-panel', 390, 310, 300, 690, '#CE969C', C.redFill);
    region('q3-panel', 758, 310, 300, 690, '#78AAA9', C.cyanFill);
    for (const [i, x] of [[1, 22], [2, 390], [3, 758]]) {
        text(`q${i}-title`, x, 328, 300, 40, `问题${i}`, 31);
    }
    box('q1-heading', 40, 386, 264, 98, '移步异景\n趣味性建模', {size: 30});
    box('q2-heading', 408, 386, 264, 98, '小中见大\n幻境感建模', {size: 30});
    box('q3-heading', 776, 386, 264, 98, '有法无式\n相似度建模', {size: 30});
    hollow('q1-down', 172, 493, 54, 42);
    hollow('q2-down', 540, 493, 54, 42);
    hollow('q3-down', 908, 493, 54, 42);
    text('q1-skeleton', 30, 502, 115, 34, '骨架提取', 24);
    text('q1-graph', 199, 502, 115, 34, '图建模', 24);
    text('q2-grid', 391, 502, 132, 34, '单元格划分', 24);
    text('q2-feature', 564, 502, 120, 34, '结构特征', 24);
    box('q1-key', 75, 564, 194, 66, '游线关键特征', {size: 26});
    box('q2-cluster', 443, 564, 194, 66, '聚类算法', {size: 27});
    box('q3-quantify', 807, 564, 202, 66, '相似性量化', {size: 27});

    region('q1-metrics', 34, 658, 276, 90, '#6F88B5', '#FFFFFF');
    box('q1-variety', 45, 677, 110, 51, '异景程度', {size: 24, fill: '#E8EFFB'});
    box('q1-interest', 168, 677, 134, 51, '趣味性分析', {size: 24, fill: '#E8EFFB'});
    arrow('key-metrics', [[172, 635], [172, 653]], ids['q1-key'], roles['q1-metrics']);
    hollow('q1-model-down', 172, 757, 48, 42);
    text('q1-genetic', 25, 764, 122, 32, '遗传算法', 24);
    box('q1-plan', 93, 823, 158, 56, '规划模型', {size: 26});
    box('q1-compare', 93, 914, 158, 56, '差异对比', {size: 26});
    arrow('plan-compare', [[172, 884], [172, 909]], ids['q1-plan'], ids['q1-compare']);

    region('q2-space', 408, 652, 264, 138, C.red, 'transparent', true);
    box('q2-change', 462, 668, 156, 40, '开合变化', {size: 25});
    box('q2-open', 421, 734, 114, 40, '开阔度', {size: 24, fill: '#FCE3E1'});
    box('q2-close', 549, 734, 110, 40, '围合度', {size: 24, fill: '#FCE3E1'});
    arrow('cluster-change', [[540, 635], [540, 663]], ids['q2-cluster'], ids['q2-change']);
    arrow('change-open', [[501, 713], [501, 719], [478, 719], [478, 729]], ids['q2-change'], ids['q2-open'], {start: [.25, 1]});
    arrow('change-close', [[579, 713], [579, 719], [604, 719], [604, 729]], ids['q2-change'], ids['q2-close'], {start: [.75, 1]});
    region('q2-perception', 408, 810, 264, 120, C.red, 'transparent', true);
    box('q2-evaluation', 447, 819, 186, 38, '幻境感知评价', {size: 25});
    box('q2-elements', 421, 879, 114, 40, '元素分布', {size: 24, fill: '#FCE3E1'});
    box('q2-rhythm', 549, 879, 110, 40, '开合节律', {size: 24, fill: '#FCE3E1'});
    arrow('space-perception', [[540, 794], [540, 814]], roles['q2-space'], ids['q2-evaluation']);
    arrow('elements-evaluate', [[478, 874], [478, 862]], ids['q2-elements'], ids['q2-evaluation'], {start: [.5, 0], end: [.17, 1]});
    arrow('rhythm-evaluate', [[604, 874], [604, 862]], ids['q2-rhythm'], ids['q2-evaluation'], {start: [.5, 0], end: [.84, 1]});
    box('q2-ranking', 447, 947, 186, 40, '幻境评分排名', {size: 24});
    arrow('perception-ranking', [[540, 934], [540, 942]], roles['q2-perception'], ids['q2-ranking']);

    box('q3-common', 791, 681, 234, 67, '共性美学特征表达', {size: 26});
    box('q3-validation', 784, 805, 248, 79, '泛化验证\n以留出园林为例', {size: 26});
    box('q3-description', 807, 919, 202, 55, '多元美学刻画', {size: 26});
    arrow('quantify-common', [[908, 635], [908, 676]], ids['q3-quantify'], ids['q3-common']);
    arrow('common-validation', [[908, 753], [908, 800]], ids['q3-common'], ids['q3-validation']);
    arrow('validation-description', [[908, 889], [908, 914]], ids['q3-validation'], ids['q3-description']);
    // 不穿过节点的专用走线区：左侧结果接右侧验证；虚线回返到幻境感知。
    arrow('q1-to-validation', [[256, 851], [348, 851], [348, 1021], [1046, 1021], [1046, 845], [1037, 845]],
        ids['q1-plan'], ids['q3-validation'], {color: C.cyan, start: [1, .5], end: [1, .5]});
    arrow('q2-to-validation', [[638, 838], [708, 838], [708, 828], [779, 828]],
        ids['q2-evaluation'], ids['q3-validation'], {color: C.red, start: [1, .5], end: [0, .29]});
    arrow('validation-feedback', [[779, 865], [728, 865], [728, 904], [664, 904]],
        ids['q3-validation'], ids['q2-rhythm'], {color: C.red, dashed: true, start: [0, .76], end: [1, .6]});

    region('summary', 0, 1098, 1080, 214, C.gold, '#FFFFFF');
    for (const [x, role, value] of [[62, 'interest', '趣味性'], [430, 'fantasy', '幻境感'], [798, 'similarity', '相似度']]) {
        box(`summary-${role}`, x, 1130, 220, 68, value, {color: C.gold, size: 30});
        hollow(`summary-arrow-${role}`, x + 110, 1047, 71, 64);
    }
    box('summary-conclusion', 242, 1227, 596, 60, '江 南 古 典 园 林 美 学 特 征', {color: C.gold, size: 28});
}

/** 锁定目标文件所在视图，等待真实画布 API 就绪。 */
async function openView() {
    const file = app.vault.getAbstractFileByPath(PATH);
    if (!file) throw new Error(`未找到 ${PATH}`);
    let leaf = app.workspace.getLeavesOfType('excalidraw').find(l => l.view.file?.path === PATH);
    if (!leaf) { leaf = app.workspace.getLeaf('tab'); await leaf.openFile(file); }
    app.workspace.setActiveLeaf(leaf, {focus: true});
    for (let i = 0; i < 150; i++) {
        const loadedLeaf = app.workspace.getLeavesOfType('excalidraw').find(l => l.view.file?.path === PATH);
        if (loadedLeaf?.view?._loaded && loadedLeaf.view.excalidrawAPI) {
            ea.setView(loadedLeaf.view);
            return ea.getExcalidrawAPI();
        }
        await new Promise(r => setTimeout(r, 100));
    }
    throw new Error('目标绘图尚未载入，可稍后 inspect；不要重复创建');
}

/** 保存纯原生场景作为交换副本，同时统计元素。 */
async function snapshot(suffix = '') {
    const api = await openView();
    const elements = api.getSceneElements();
    const scene = {type: 'excalidraw', version: 2,
        source: 'https://github.com/zsviczian/obsidian-excalidraw-plugin', elements,
        appState: {viewBackgroundColor: '#FFFFFF', theme: 'light', gridSize: null}, files: api.getFiles()};
    await app.vault.adapter.write(`${BASE}/${STEM}${suffix}.excalidraw`, JSON.stringify(scene, null, 2));
    ea.viewZoomToElements(true, elements);
    return {count: elements.length, types: Object.fromEntries([...new Set(elements.map(e => e.type))]
        .map(t => [t, elements.filter(e => e.type === t).length])), path: PATH};
}

/** 新建独立源图；已有同名图时拒绝覆盖。 */
async function create() {
    if (app.vault.getAbstractFileByPath(PATH)) throw new Error('样图已存在，拒绝覆盖人工编辑');
    build();
    const count = ea.getElements().length;
    await ea.create({filename: `${STEM}.excalidraw.md`, foldername: BASE, silent: true,
        frontmatterKeys: {'excalidraw-plugin': 'parsed', 'excalidraw-export-transparent': false,
            'excalidraw-export-dark': false, 'excalidraw-export-padding': 24,
            'excalidraw-export-pngscale': 3, 'excalidraw-export-embed-scene': true}});
    ea.clear();
    return {created: PATH, count};
}

/** 在真实画布上修改文字及一个子节点位置，保留 ID 和连线。 */
async function edit() {
    await openView();
    const before = ea.getViewElements();
    const lookup = role => before.find(e => e.customData?.paperFlowRole === role);
    const target = lookup('q2-rhythm-text');
    if (target.originalText !== '开合节律') throw new Error('编辑已执行或文字被用户修改，拒绝覆盖');
    await snapshot('.before-edit');
    ea.clear();
    ea.copyViewElementsToEAforEditing(before);
    const t = ea.getElement(target.id);
    t.text = t.originalText = t.rawText = '开合节奏';
    for (const role of ['q2-elements', 'q2-elements-text', 'q2-rhythm', 'q2-rhythm-text']) {
        ea.getElement(lookup(role).id).y += 3;
    }
    const changed = await ea.addElementsToView(false, true, false, true);
    if (!changed) throw new Error('插件未确认保存');
    await flushSave();
    ea.clear();
    const after = ea.getViewElements();
    const record = {date: new Date().toISOString(), source: PATH, textBefore: '开合节律', textAfter: '开合节奏',
        childNodesMovedDown: 3, idsPreserved: before.map(e => e.id).sort().join() === after.map(e => e.id).sort().join(),
        method: 'copyViewElementsToEAforEditing + addElementsToView', pluginVersion: ea.plugin.manifest.version};
    await snapshot();
    await app.vault.adapter.write(`${BASE}/${STEM}.edit-check.json`, JSON.stringify(record, null, 2));
    return record;
}

/** 比较几何及文字，避免保存尚未完成时静默导出旧场景。 */
function sceneKey(elements) {
    return JSON.stringify(elements.filter(e => !e.isDeleted).map(e => ({
        id: e.id, type: e.type, x: e.x, y: e.y, width: e.width, height: e.height,
        text: e.text, originalText: e.originalText, fontSize: e.fontSize,
        points: e.points, startBinding: e.startBinding, endBinding: e.endBinding,
        strokeColor: e.strokeColor, backgroundColor: e.backgroundColor, strokeStyle: e.strokeStyle,
    })).sort((a, b) => a.id.localeCompare(b.id)));
}

/**
 * 强制把当前画布写回源文件。
 * 通过 EA 修改场景后，插件的自动保存可能不在检查窗口内触发；
 * 2.26.4 上显式 setDirty + save 才会立即落盘，这一区别已实测。
 */
async function flushSave() {
    const leaf = app.workspace.getLeavesOfType('excalidraw').find(l => l.view.file?.path === PATH);
    if (!leaf) throw new Error('未找到目标 Excalidraw 视图');
    app.workspace.setActiveLeaf(leaf, {focus: true});
    ea.setView(leaf.view);
    if (typeof leaf.view.setDirty === 'function') leaf.view.setDirty();
    if (typeof leaf.view.save === 'function') await leaf.view.save();
    else if (typeof leaf.view.forceSave === 'function') await leaf.view.forceSave();
    await new Promise(resolve => setTimeout(resolve, 300));
    return {dirty: typeof leaf.view.isDirty === 'function' ? leaf.view.isDirty() : null};
}

/** 限时等待保存；不在待保存状态生成可交付文件。 */
async function checkSaved() {
    await openView();
    await flushSave();
    const file = app.vault.getAbstractFileByPath(PATH);
    for (let i = 0; i < 20; i++) {
        const saved = await ea.getSceneFromFile(file);
        if (sceneKey(saved.elements) === sceneKey(ea.getViewElements())) return saved;
        await new Promise(resolve => setTimeout(resolve, 200));
    }
    throw new Error('源文件与画布仍不一致，请完成保存后再导出');
}

/** 导出保存后的场景，使用实际插件渲染引擎而非网页截图。 */
async function exportFigure() {
    const saved = await checkSaved();
    if (saved.elements.some(e => e.type === 'image')) throw new Error('本测试仅支持无嵌入图片的原生图');
    const sourceText = await app.vault.adapter.read(PATH);
    ea.clear();
    const settings = {withBackground: true, withTheme: true, isMask: false};
    const svg = await ea.createSVG(PATH, true, settings, undefined, 'light', 24);
    const png = await ea.createPNG(PATH, 3, settings, undefined, 'light', 24);
    if (!svg || !png) throw new Error('未返回导出结果');
    if (sourceText !== await app.vault.adapter.read(PATH)) throw new Error('导出期间源文件改变，请重试');
    await app.vault.adapter.write(`${BASE}/${STEM}.svg`, new XMLSerializer().serializeToString(svg));
    await app.vault.adapter.writeBinary(`${BASE}/${STEM}.png`, await png.arrayBuffer());
    const record = {source: PATH, engine: 'ExcalidrawAutomate.createSVG/createPNG',
        pluginVersion: ea.plugin.manifest.version, exportedAt: new Date().toISOString(),
        width: svg.getAttribute('width'), height: svg.getAttribute('height'), pngScale: 3, ...await snapshot()};
    await app.vault.adapter.write(`${BASE}/${STEM}.export.json`, JSON.stringify(record, null, 2));
    return record;
}

/** 判定元素角色属于哪套配色主题；返回 null 表示不参与重着色。 */
function natureTheme(role) {
    if (!role) return null;
    if (NATURE_EXPLICIT[role]) return NATURE_EXPLICIT[role];
    if (NATURE_DATA_ROLES.has(role)) return 'data';
    if (/^q[123]/.test(role)) return role.slice(0, 2);
    if (role.startsWith('summary')) return 'summary';
    // 大标题保持近黑，避免整幅图只剩彩色描边。
    if (role === 'preprocess-title') return null;
    if (role.startsWith('preprocess')) return 'data';
    return null;
}

/**
 * 按科研期刊配色重着色现有元素。
 * 只改颜色属性，保留元素 ID、文字、尺寸和全部端点绑定；
 * 虚线框和透明填充维持原样，避免配色修改改变图的语义层级。
 */
async function recolor() {
    await openView();
    await snapshot('.before-nature');
    const scene = ea.getViewElements();
    const lookup = Object.fromEntries(scene.map(e => [e.id, e]));
    ea.clear();
    ea.copyViewElementsToEAforEditing(scene);
    const changed = [];
    for (const el of scene) {
        const role = el.customData?.paperFlowRole;
        const themeName = natureTheme(role);
        const target = ea.getElement(el.id);
        if (!themeName) {
            if (el.type === 'text') {
                target.strokeColor = NATURE.ink;
                changed.push({role, type: el.type, stroke: NATURE.ink});
            }
            continue;
        }
        const theme = NATURE_THEME[themeName];
        if (el.type === 'text') {
            target.strokeColor = /^q[123]-title$/.test(role) ? theme.stroke : NATURE.ink;
        } else {
            target.strokeColor = theme.stroke;
            if (el.type === 'rectangle' || el.type === 'line') {
                const keptTransparent = el.backgroundColor === 'transparent';
                target.backgroundColor = keptTransparent
                    ? 'transparent'
                    : (NATURE_TINT.has(role) ? theme.fill : NATURE.white);
            }
        }
        changed.push({role, type: el.type, theme: themeName, stroke: target.strokeColor,
            fill: target.backgroundColor});
    }
    // 文字是独立元素，容器填充变化后重新居中，避免配色步骤引入新的换行。
    for (const el of scene) {
        const role = el.customData?.paperFlowRole;
        if (!el.containerId) continue;
        const holder = lookup[el.containerId];
        if (!holder) continue;
        const t = ea.getElement(el.id);
        const m = ea.measureText(t.originalText ?? t.text);
        t.x = holder.x + (holder.width - m.width) / 2;
        t.y = holder.y + (holder.height - m.height) / 2;
        changed.push({role, type: 'recenter', width: m.width, height: m.height});
    }
    const saved = await ea.addElementsToView(false, true, false, true);
    if (!saved) throw new Error('插件未确认配色保存');
    await flushSave();
    ea.clear();
    const record = {date: new Date().toISOString(), source: PATH,
        palette: 'NPG (Nature Publishing Group) low-saturation',
        paletteValues: {...NATURE}, changedElements: changed.filter(c => c.type !== 'recenter').length,
        recenteredTexts: changed.filter(c => c.type === 'recenter').length,
        idsPreserved: scene.map(e => e.id).sort().join() === ea.getViewElements().map(e => e.id).sort().join(),
        method: 'copyViewElementsToEAforEditing + addElementsToView'};
    await snapshot();
    await app.vault.adapter.write(`${BASE}/${STEM}.recolor-check.json`, JSON.stringify(record, null, 2));
    return record;
}

/** 将导出检查发现的换行、对齐问题修复到现有图，保留修订前场景。 */
async function polish() {
    await openView();
    await snapshot('.before-layout');
    const scene = ea.getViewElements();
    const byRole = role => scene.find(e => e.customData?.paperFlowRole === role);
    ea.clear();
    ea.copyViewElementsToEAforEditing(scene);
    const edits = {
        'q1-metrics': {x: 34, y: 658, width: 276, height: 90},
        'q1-variety': {x: 45, y: 677, width: 110, height: 51},
        'q1-interest': {x: 168, y: 677, width: 134, height: 51},
        'q2-heading': {x: 408, y: 386},
        'q2-cluster': {x: 443, y: 564},
        'q1-panel': {height: 690}, 'q2-panel': {height: 690}, 'q3-panel': {height: 690},
        'q2-ranking': {height: 40},
    };
    for (const [role, changes] of Object.entries(edits)) {
        const shape = ea.getElement(byRole(role).id);
        Object.assign(shape, changes);
        const bound = shape.boundElements?.find(e => e.type === 'text');
        if (bound) {
            const t = ea.getElement(bound.id);
            const size = role === 'q1-interest' ? 24 : t.fontSize;
            style({fontSize: size});
            const m = ea.measureText(t.originalText);
            Object.assign(t, {fontSize: size, text: t.originalText, width: m.width, height: m.height,
                x: shape.x + (shape.width - m.width) / 2, y: shape.y + (shape.height - m.height) / 2});
        }
    }
    // 修正连接至聚类节点的箭头，使端点与对齐后的节点一致。
    const a = ea.getElement(byRole('cluster-change').id);
    Object.assign(a, {x: 540, y: 635, width: 0, height: 28, points: [[0, 0], [0, 28]]});
    await ea.addElementsToView(false, true, false, true);
    await flushSave();
    ea.clear();
    return await snapshot();
}

if (mode === 'check-saved') { const saved = await checkSaved(); return {savedMatchesCanvas: true, elements: saved.elements.length}; }
if (mode === 'recolor') return await recolor();
if (mode === 'polish') return await polish();
if (mode === 'create') return await create();
if (mode === 'inspect') return await snapshot();
if (mode === 'edit') return await edit();
if (mode === 'export') return await exportFigure();
throw new Error('支持的 mode: create / inspect / edit / polish / recolor / check-saved / export');

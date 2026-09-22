/**
 * 小流程图：中文节点、是/否分支、修正反馈箭头，Nature/NPG 科研配色。
 *
 * create 新建并保存源图；export 先把画布写回源文件，再导出 SVG 与 3 倍 PNG。
 * 调用方注入 ea、app、mode。所有元素都是原生 rectangle/diamond/text/arrow，
 * 可在 Obsidian 中逐项编辑；不调用网络或 AI 服务。
 */
const BASE = '20_学习/研究生数模竞赛/skills/huawei-math-modeling/assets';
const STEM = 'excalidraw-simple-flow';
const PATH = `${BASE}/${STEM}.excalidraw.md`;

/** NPG（Nature Publishing Group）低饱和科研配色。 */
const N = {
    ink: '#1A1A1A',
    structure: '#3C5488',
    data: '#4DBBD5',
    emphasis: '#B5534A',
    validate: '#00A087',
    summary: '#B09C85',
    fillStructure: '#EDF1F7',
    fillData: '#EAF6FA',
    fillEmphasis: '#FBEDEA',
    fillValidate: '#E7F4F1',
    white: '#FFFFFF',
};
const ids = {};

/** 重置新元素样式，避免虚实线或填充在元素之间泄漏。 */
function style(options = {}) {
    Object.assign(ea.style, {
        strokeColor: N.structure, backgroundColor: N.white, fillStyle: 'solid',
        strokeWidth: 1.8, strokeStyle: 'solid', roughness: 0, roundness: null,
        fontFamily: 2, fontSize: 27, textAlign: 'center', verticalAlign: 'middle',
        startArrowHead: null, endArrowHead: 'triangle', ...options,
    });
}

/** 附加语义角色，便于后续按角色定位元素。 */
function tag(id, role) {
    ea.addAppendUpdateCustomData(id, {paperFlowRole: role});
    ids[role] = id;
    return id;
}

/** 居中放置可编辑文字，并校验它确实放得下。 */
function text(role, x, y, w, h, value, fontSize = 27, color = N.ink) {
    style({fontSize, strokeColor: color});
    const size = ea.measureText(value);
    if (size.width > w || size.height > h) {
        throw new Error(`文字超出预留区域 ${role}: ${size.width}x${size.height} / ${w}x${h}`);
    }
    return tag(ea.addText(x + (w - size.width) / 2, y + (h - size.height) / 2, value), role);
}

/** 矩形节点，文字与容器双向绑定。 */
function box(role, x, y, w, h, value, options = {}) {
    const {color = N.structure, fill = N.white, size = 27} = options;
    style({strokeColor: color, backgroundColor: fill});
    const id = tag(ea.addRect(x, y, w, h), role);
    const label = text(`${role}-text`, x + 8, y + 6, w - 16, h - 12, value, size);
    const holder = ea.getElement(id);
    holder.boundElements = [{type: 'text', id: label}];
    ea.getElement(label).containerId = id;
    return id;
}

/** 菱形判断节点。 */
function diamond(role, x, y, w, h, value, options = {}) {
    const {color = N.structure, fill = N.fillStructure, size = 26} = options;
    style({strokeColor: color, backgroundColor: fill});
    const id = tag(ea.addDiamond(x, y, w, h), role);
    // 菱形内部可用宽度约为外接矩形的一半，按此预留再居中。
    const label = text(`${role}-text`, x + w * 0.25, y + h * 0.25, w * 0.5, h * 0.5, value, size);
    const holder = ea.getElement(id);
    holder.boundElements = [{type: 'text', id: label}];
    ea.getElement(label).containerId = id;
    return id;
}

/** 折线箭头；可绑定起点和终点元素。 */
function arrow(role, points, fromId, toId, options = {}) {
    const {color = N.structure, dashed = false, start = [0.5, 1], end = [0.5, 0]} = options;
    style({strokeColor: color, strokeWidth: 1.9, strokeStyle: dashed ? 'dashed' : 'solid'});
    const binding = {};
    if (fromId) Object.assign(binding, {startObjectId: fromId, startFixedPoint: start, startBindMode: 'orbit'});
    if (toId) Object.assign(binding, {endObjectId: toId, endFixedPoint: end, endBindMode: 'orbit'});
    return tag(ea.addArrow(points, {...binding, startArrowHead: null, endArrowHead: 'triangle',
        elbowed: false}), role);
}

/** 画出全部节点与连线。 */
function build() {
    ea.reset();
    ea.canvas.theme = 'light';
    ea.canvas.viewBackgroundColor = N.white;

    const a = box('parse', 320, 0, 340, 64, '题意解析与目标确定');
    const b = box('data', 320, 104, 340, 64, '数据核对与预处理',
        {color: N.data, fill: N.fillData});
    const c = box('plan', 320, 208, 340, 64, '讨论并确定模型方案');
    const baseline = box('baseline', 60, 340, 330, 68, '基线模型');
    const innovation = box('innovation', 590, 340, 330, 68, '创新模型',
        {color: N.emphasis, fill: N.fillEmphasis});
    const check = box('check', 320, 470, 340, 68, '小样本实现与核验',
        {color: N.validate, fill: N.fillValidate});
    const gate = diamond('gate', 320, 600, 340, 160, '精度与稳健性\n是否达标？', {size: 24});
    const output = box('output', 320, 820, 340, 64, '全量实验与论文图表',
        {color: N.summary, fill: N.white});

    arrow('parse-data', [[490, 66], [490, 100]], a, b);
    arrow('data-plan', [[490, 170], [490, 204]], b, c);
    // 分支：从方案节点下沿左右两处出发，绕开中间区域后在两侧落下。
    arrow('plan-baseline', [[400, 274], [400, 310], [225, 310], [225, 336]], c, baseline,
        {start: [0.24, 1]});
    arrow('plan-innovation', [[580, 274], [580, 310], [755, 310], [755, 336]], c, innovation,
        {start: [0.76, 1]});
    arrow('baseline-check', [[225, 410], [225, 440], [400, 440], [400, 466]], baseline, check,
        {end: [0.24, 0]});
    arrow('innovation-check', [[755, 410], [755, 440], [580, 440], [580, 466]], innovation, check,
        {end: [0.76, 0]});
    arrow('check-gate', [[490, 540], [490, 598]], check, gate);
    arrow('gate-output', [[490, 762], [490, 816]], gate, output);
    // 反馈回路：判断不通过时回到方案讨论，走右侧专用通道，不穿过其它节点。
    arrow('feedback', [[660, 680], [980, 680], [980, 240], [662, 240]], gate, c,
        {color: N.emphasis, dashed: true, start: [1, 0.5], end: [1, 0.5]});

    text('gate-output-label', 500, 778, 70, 30, '是', 23);
    text('feedback-label', 700, 632, 250, 34, '否：修正模型方案', 22, N.emphasis);
}

/** 打开源图并等待画布可用。 */
async function openView() {
    const file = app.vault.getAbstractFileByPath(PATH);
    if (!file) throw new Error(`未找到 ${PATH}`);
    let leaf = app.workspace.getLeavesOfType('excalidraw').find(l => l.view.file?.path === PATH);
    if (!leaf) {
        leaf = app.workspace.getLeaf('tab');
        await leaf.openFile(file);
    }
    app.workspace.setActiveLeaf(leaf, {focus: true});
    for (let i = 0; i < 150; i++) {
        const current = app.workspace.getLeavesOfType('excalidraw')
            .find(l => l.view.file?.path === PATH);
        if (current?.view?._loaded && current.view.excalidrawAPI) {
            ea.setView(current.view);
            return ea.getExcalidrawAPI();
        }
        await new Promise(resolve => setTimeout(resolve, 100));
    }
    throw new Error('绘图尚未载入，稍后重试；不要重复创建');
}

/**
 * 强制把画布写回源文件。
 * 实测 2.26.4：通过 EA 改场景后自动保存未必在检查窗口内触发，
 * 必须先 setDirty 再 await save，否则导出的是旧图。
 */
async function flushSave() {
    const leaf = app.workspace.getLeavesOfType('excalidraw').find(l => l.view.file?.path === PATH);
    if (!leaf) throw new Error('未找到目标视图');
    app.workspace.setActiveLeaf(leaf, {focus: true});
    ea.setView(leaf.view);
    if (typeof leaf.view.setDirty === 'function') leaf.view.setDirty();
    if (typeof leaf.view.save === 'function') await leaf.view.save();
    else if (typeof leaf.view.forceSave === 'function') await leaf.view.forceSave();
    await new Promise(resolve => setTimeout(resolve, 300));
}

/** 画布与源文件的几何、文字、颜色必须一致，否则不导出。 */
function sceneKey(elements) {
    return JSON.stringify(elements.filter(e => !e.isDeleted).map(e => ({
        id: e.id, type: e.type, x: e.x, y: e.y, width: e.width, height: e.height,
        text: e.text, originalText: e.originalText, points: e.points,
        startBinding: e.startBinding, endBinding: e.endBinding,
        strokeColor: e.strokeColor, backgroundColor: e.backgroundColor, strokeStyle: e.strokeStyle,
    })).sort((a, b) => a.id.localeCompare(b.id)));
}

/** 新建源图；同名文件已存在时拒绝覆盖。 */
async function create() {
    if (app.vault.getAbstractFileByPath(PATH)) {
        throw new Error('源图已存在，拒绝覆盖；如需重建请先确认');
    }
    build();
    const count = ea.getElements().length;
    await ea.create({
        filename: `${STEM}.excalidraw.md`,
        foldername: BASE,
        silent: true,
        frontmatterKeys: {
            'excalidraw-plugin': 'parsed',
            'excalidraw-export-transparent': false,
            'excalidraw-export-dark': false,
            'excalidraw-export-padding': 24,
            'excalidraw-export-pngscale': 3,
            'excalidraw-export-embed-scene': true,
        },
    });
    ea.clear();
    await openView();
    ea.viewZoomToElements(true, ea.getViewElements());
    return {created: PATH, elements: count, palette: 'NPG low-saturation'};
}

/** 保存校验通过后导出 SVG 与 PNG。 */
async function exportFigure() {
    await openView();
    await flushSave();
    const file = app.vault.getAbstractFileByPath(PATH);
    let matched = false;
    let savedElements = [];
    for (let i = 0; i < 20; i++) {
        const saved = await ea.getSceneFromFile(file);
        savedElements = saved.elements;
        if (sceneKey(saved.elements) === sceneKey(ea.getViewElements())) {
            matched = true;
            break;
        }
        await flushSave();
        await new Promise(resolve => setTimeout(resolve, 200));
    }
    if (!matched) throw new Error('画布与源文件不一致，已停止导出');
    ea.clear();
    const settings = {withBackground: true, withTheme: true, isMask: false};
    const svg = await ea.createSVG(PATH, true, settings, undefined, 'light', 24);
    const png = await ea.createPNG(PATH, 3, settings, undefined, 'light', 24);
    if (!svg || !png) throw new Error('未返回导出结果');
    await app.vault.adapter.write(`${BASE}/${STEM}.svg`, new XMLSerializer().serializeToString(svg));
    await app.vault.adapter.writeBinary(`${BASE}/${STEM}.png`, await png.arrayBuffer());
    const kinds = {};
    for (const e of savedElements) kinds[e.type] = (kinds[e.type] ?? 0) + 1;
    const record = {
        source: PATH,
        engine: 'ExcalidrawAutomate.createSVG/createPNG',
        pluginVersion: ea.plugin.manifest.version,
        exportedAt: new Date().toISOString(),
        elements: savedElements.length,
        typeCounts: kinds,
        everyArrowBound: savedElements.filter(e => e.type === 'arrow')
            .every(e => e.startBinding?.elementId && e.endBinding?.elementId),
        svgSize: [Number(svg.getAttribute('width')), Number(svg.getAttribute('height'))],
        pngScale: 3,
        palette: 'NPG (Nature Publishing Group) low-saturation',
    };
    await app.vault.adapter.write(`${BASE}/${STEM}.export.json`, JSON.stringify(record, null, 2));
    return record;
}

if (mode === 'create') return await create();
if (mode === 'export') return await exportFigure();
throw new Error('支持的 mode: create / export');

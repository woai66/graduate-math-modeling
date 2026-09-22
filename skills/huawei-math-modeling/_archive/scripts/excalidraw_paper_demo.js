/**
 * 在 Obsidian ExcalidrawAutomate 中创建、编辑和导出论文流程图测试件。
 * create 生成独立中文节点与绑定箭头；edit 对现有元素保留 ID 进行修改；
 * export 从已保存的源图导出 SVG/PNG。只写本测试的固定资产，不调用 AI 服务。
 * 调用器注入 ea、app、mode；脚本不自动修改已有人工编辑的图。
 */
const BASE = '20_学习/研究生数模竞赛/skills/huawei-math-modeling/assets';
const STEM = 'excalidraw-paper-flow';
const DRAWING = `${BASE}/${STEM}.excalidraw.md`;
const EXPORT_SETTINGS = {withBackground: true, withTheme: true, isMask: false};

/** 将节点的语义标识附到已有 customData 上。 */
function tag(id, role) {
    ea.addAppendUpdateCustomData(id, {paperFlowRole: role});
    return id;
}

/** 创建可独立编辑文字、大小和连接的原生容器节点。 */
function node(role, x, y, w, h, text, type = 'rectangle') {
    const shape = type === 'diamond' ? ea.addDiamond(x, y, w, h) : ea.addRect(x, y, w, h);
    const size = ea.measureText(text);
    const label = ea.addText(x + (w - size.width) / 2, y + (h - size.height) / 2, text);
    const t = ea.getElement(label);
    // 不同版本的 measureText 返回 w/h 或 width/height，最终以文本实际尺寸居中。
    t.x = x + (w - t.width) / 2;
    t.y = y + (h - t.height) / 2;
    t.textAlign = 'center';
    t.verticalAlign = 'middle';
    t.containerId = shape;
    ea.getElement(shape).boundElements = [{type: 'text', id: label}];
    tag(shape, role);
    tag(label, `${role}-text`);
    return shape;
}

/** 创建两端固定到原生节点的折线箭头。 */
function arrow(role, points, from, to, start, end) {
    return tag(ea.addArrow(points, {
        startObjectId: from, endObjectId: to,
        startFixedPoint: start, endFixedPoint: end,
        startBindMode: 'orbit', endBindMode: 'orbit',
        startArrowHead: null, endArrowHead: 'triangle', elbowed: false,
    }), role);
}

/** 保存不含嵌入图片的原生场景，便于应用外交换与逐元素核对。 */
async function snapshot(suffix) {
    const api = ea.getExcalidrawAPI();
    const scene = {
        type: 'excalidraw', version: 2,
        source: 'https://github.com/zsviczian/obsidian-excalidraw-plugin',
        elements: api.getSceneElements(),
        appState: {viewBackgroundColor: '#ffffff', theme: 'light', gridSize: null},
        files: api.getFiles(),
    };
    await app.vault.adapter.write(`${BASE}/${STEM}${suffix}.excalidraw`, JSON.stringify(scene, null, 2));
    return scene;
}

/** 找到本测试绘图并等待画布载入，避免编辑用户当前打开的其他图。 */
async function openDrawing() {
    const file = app.vault.getAbstractFileByPath(DRAWING);
    if (!file) throw new Error(`未找到测试图：${DRAWING}`);
    let leaf = app.workspace.getLeavesOfType('excalidraw').find(l => l.view.file?.path === DRAWING);
    if (!leaf) {
        leaf = app.workspace.getLeaf('tab');
        await leaf.openFile(file);
    }
    app.workspace.setActiveLeaf(leaf, {focus: true});
    for (let i = 0; i < 100 && (!leaf.view._loaded || !leaf.view.excalidrawAPI); i++) {
        await new Promise(r => setTimeout(r, 100));
    }
    ea.setView(leaf.view);
    if (!ea.getExcalidrawAPI()) throw new Error('Excalidraw 画布未载入');
}

/** 创建首次版本；已有图时拒绝覆盖。 */
async function createDrawing() {
    if (app.vault.getAbstractFileByPath(DRAWING)) throw new Error('测试图已存在，请使用 edit/export');
    ea.reset();
    Object.assign(ea.style, {
        strokeColor: '#202020', backgroundColor: '#ffffff',
        fillStyle: 'solid', strokeWidth: 1.8, roughness: 0,
        fontFamily: 2, fontSize: 26, roundness: null,
    });
    ea.canvas.theme = 'light';
    ea.canvas.viewBackgroundColor = '#ffffff';
    const n = {};
    n.start = node('start', 260, 0, 300, 60, '题意解析与目标确定');
    n.data = node('data', 260, 100, 300, 60, '数据核对与预处理');
    n.plan = node('plan', 260, 200, 300, 60, '讨论并确定模型方案');
    n.base = node('baseline', 60, 320, 280, 68, '基线模型');
    n.idea = node('innovation', 480, 320, 280, 68, '创新模型');
    n.check = node('check', 260, 450, 300, 68, '小样本实现与核验');
    n.gate = node('gate', 260, 570, 300, 130, '检验是否\n满足要求？', 'diamond');
    n.output = node('output', 260, 790, 300, 60, '全量实验与论文图表');
    arrow('start-data', [[410, 65], [410, 95]], n.start, n.data, [.5, 1], [.5, 0]);
    arrow('data-plan', [[410, 165], [410, 195]], n.data, n.plan, [.5, 1], [.5, 0]);
    arrow('plan-baseline', [[360, 265], [360, 290], [200, 290], [200, 315]], n.plan, n.base, [1/3, 1], [.5, 0]);
    arrow('plan-innovation', [[460, 265], [460, 290], [620, 290], [620, 315]], n.plan, n.idea, [2/3, 1], [.5, 0]);
    arrow('baseline-check', [[200, 393], [200, 425], [360, 425], [360, 445]], n.base, n.check, [.5, 1], [1/3, 0]);
    arrow('innovation-check', [[620, 393], [620, 425], [460, 425], [460, 445]], n.idea, n.check, [.5, 1], [2/3, 0]);
    arrow('check-gate', [[410, 523], [410, 565]], n.check, n.gate, [.5, 1], [.5, 0]);
    arrow('accepted', [[410, 705], [410, 785]], n.gate, n.output, [.5, 1], [.5, 0]);
    arrow('feedback', [[565, 635], [830, 635], [830, 230], [565, 230]], n.gate, n.plan, [1, .5], [1, .5]);
    tag(ea.addText(430, 730, '是'), 'accepted-label');
    tag(ea.addText(670, 492, '否：修正方案'), 'feedback-label');
    const created = await ea.create({
        filename: `${STEM}.excalidraw.md`, foldername: BASE, silent: true,
        frontmatterKeys: {
            'excalidraw-plugin': 'parsed', 'excalidraw-export-transparent': false,
            'excalidraw-export-dark': false, 'excalidraw-export-padding': 24,
            'excalidraw-export-pngscale': 3, 'excalidraw-export-embed-scene': true,
        },
    });
    ea.clear();
    await openDrawing();
    const initial = await snapshot('.initial');
    ea.viewZoomToElements(true, initial.elements);
    return {created, elements: initial.elements.length, status: 'created_in_obsidian'};
}

/** 真实修改现有节点和反馈线，保留元素身份、容器关系与端点绑定。 */
async function editDrawing() {
    await openDrawing();
    const before = ea.getViewElements();
    const find = role => before.find(e => e.customData?.paperFlowRole === role);
    const target = find('innovation');
    if (!target) throw new Error('缺少创新分支节点');
    if (find('innovation-text').originalText === '创新机制候选') throw new Error('编辑测试已经执行');
    ea.clear();
    ea.copyViewElementsToEAforEditing(before);
    const updates = [];
    for (const role of ['innovation', 'innovation-text']) {
        const el = ea.getElement(find(role).id);
        updates.push({role, oldX: el.x, newX: el.x + 20});
        el.x += 20;
    }
    const text = ea.getElement(find('innovation-text').id);
    text.text = text.originalText = text.rawText = '创新机制候选';
    text.width = 26 * 6;
    text.x = ea.getElement(target.id).x + (280 - text.width) / 2;
    const incoming = ea.getElement(find('plan-innovation').id);
    incoming.points[2][0] += 20;
    incoming.points[3][0] += 20;
    incoming.width += 20;
    const outgoing = ea.getElement(find('innovation-check').id);
    outgoing.x += 20;
    outgoing.points[2][0] -= 20;
    outgoing.points[3][0] -= 20;
    outgoing.width += 20;
    const feedback = ea.getElement(find('feedback').id);
    feedback.points[1][0] += 20;
    feedback.points[2][0] += 20;
    feedback.width += 20;
    await ea.addElementsToView(false, true, false, true);
    ea.clear();
    const final = await snapshot('');
    ea.viewZoomToElements(true, final.elements);
    const record = {
        editedAt: new Date().toISOString(), source: DRAWING,
        textChange: {before: '创新模型', after: '创新机制候选'},
        nodeTranslation: {dx: 20, dy: 0}, feedbackOuterRouteShift: 20,
        sameElementIds: before.map(e => e.id).sort().join() === final.elements.map(e => e.id).sort().join(),
        elements: final.elements.length, updateMethod: 'copyViewElementsToEAforEditing + addElementsToView',
        export: 'pending',
    };
    await app.vault.adapter.write(`${BASE}/${STEM}.edit-check.json`, JSON.stringify(record, null, 2));
    return record;
}

/** 从持久化后的源文件使用实际插件导出，不把页面截图当正式插图。 */
async function exportDrawing() {
    await openDrawing();
    ea.clear();
    const svg = await ea.createSVG(DRAWING, true, EXPORT_SETTINGS, undefined, 'light', 24);
    const png = await ea.createPNG(DRAWING, 3, EXPORT_SETTINGS, undefined, 'light', 24);
    if (!svg || !png) throw new Error('Excalidraw 导出未返回图像');
    await app.vault.adapter.write(`${BASE}/${STEM}.svg`, new XMLSerializer().serializeToString(svg));
    await app.vault.adapter.writeBinary(`${BASE}/${STEM}.png`, await png.arrayBuffer());
    const elements = ea.getViewElements();
    const record = {
        exportedAt: new Date().toISOString(), source: DRAWING,
        renderer: 'Obsidian ExcalidrawAutomate', pluginVersion: ea.plugin.manifest.version,
        svgMethod: 'createSVG(savedDrawingPath, true, ...)', pngMethod: 'createPNG(savedDrawingPath, 3, ...)',
        pngScale: 3, elementCount: elements.length,
        types: Object.fromEntries([...new Set(elements.map(e=>e.type))].map(t=>[t,elements.filter(e=>e.type===t).length])),
        svgWidth: svg.getAttribute('width'), svgHeight: svg.getAttribute('height'),
        nativeArrowBindings: elements.filter(e=>e.type==='arrow').every(e=>e.startBinding?.elementId && e.endBinding?.elementId),
    };
    await app.vault.adapter.write(`${BASE}/${STEM}.export.json`, JSON.stringify(record, null, 2));
    return record;
}

if (mode === 'snapshot-initial') { await openDrawing(); return JSON.stringify({elements: (await snapshot('.initial')).elements.length}); }
if (mode === 'create') return await createDrawing();
if (mode === 'edit') return await editDrawing();
if (mode === 'export') return await exportDrawing();
throw new Error('mode 必须为 create、edit 或 export');

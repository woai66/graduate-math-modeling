"""生成《围岩裂隙精准识别与三维模型重构》论文正式版全部插图。

所有数值图均由 results/ 下真实运行结果绘制;流程图为方法链可视化,不含任何虚构数值。
输出目录: figures/paper/
"""
from __future__ import annotations

import csv
import math
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Polygon
from PIL import Image

PROJECT = Path(__file__).resolve().parents[1]
RESULTS = PROJECT / "results"
SRC_FIGS = PROJECT / "figures" / "result"
OUT = PROJECT / "figures" / "paper"
OUT.mkdir(parents=True, exist_ok=True)

plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False
plt.rcParams["font.size"] = 11

BLUE = "#2F5597"
LIGHT_BLUE = "#EAF1FB"
TEAL = "#31859C"
ORANGE = "#C55A11"
LIGHT_ORANGE = "#FDF0E7"
GRAY = "#595959"


def read_csv(name: str) -> list[dict[str, str]]:
    with (RESULTS / name).open("r", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def rounded_box(ax, x, y, w, h, text, fc=LIGHT_BLUE, ec=BLUE, fs=10.5, bold=False, tc="#1F1F1F"):
    box = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.06",
                         linewidth=1.3, edgecolor=ec, facecolor=fc)
    ax.add_patch(box)
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fs,
            color=tc, fontweight="bold" if bold else "normal", linespacing=1.5)


def arrow(ax, x1, y1, x2, y2, color=GRAY, lw=1.4, style="-|>", ls="-"):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle=style, mutation_scale=14,
                                 linewidth=lw, color=color, linestyle=ls))


def diamond(ax, cx, cy, w, h, text, fs=9.5):
    pts = [(cx, cy + h / 2), (cx + w / 2, cy), (cx, cy - h / 2), (cx - w / 2, cy)]
    ax.add_patch(Polygon(pts, closed=True, linewidth=1.3, edgecolor=ORANGE, facecolor=LIGHT_ORANGE))
    ax.text(cx, cy, text, ha="center", va="center", fontsize=fs, color="#1F1F1F")


def new_canvas(w=10, h=7):
    fig, ax = plt.subplots(figsize=(w, h))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis("off")
    return fig, ax


# ---------------------------------------------------------------- 总体技术路线
def fig_route() -> None:
    fig, ax = new_canvas(10, 8.2)
    # 数据层
    ax.text(5, 9.75, "数据层", ha="center", fontsize=11, color=BLUE, fontweight="bold")
    for i, (label, x) in enumerate([("附件1\n10张 244×1350", 1.45), ("附件2\n10张 244×1350", 3.85),
                                    ("附件3\n11张 244×1350", 6.25), ("附件4\n6孔40段 864×9167", 8.55)]):
        rounded_box(ax, x - 1.05, 8.7, 2.1, 0.85, label, fc="#F2F2F2", ec=GRAY, fs=9)
    ax.text(5, 8.25, "SHA-256 重复检测 · 尺寸/灰度统计 · 边缘密度审计", ha="center", fontsize=9, color=GRAY)

    # 预处理层
    rounded_box(ax, 1.3, 7.0, 7.4, 0.72, "图像预处理:灰度化 → CLAHE 局部对比度增强 → 高斯/双边滤波去噪", fc="#DEEBF7")
    arrow(ax, 5, 8.62, 5, 7.78)

    # 模型层(四问)
    boxes = [
        (1.45, 4.55, "问题一\n裂隙候选分割\n黑帽+Otsu+Canny\n形态学后处理"),
        (3.85, 4.55, "问题二\n正弦参数反演\nDBSCAN 聚类\nRANSAC 鲁棒拟合"),
        (6.25, 4.55, "问题三\n粗糙度 JRC 评价\n轮廓离散化\n$Z_2$+采样敏感性"),
        (8.55, 4.55, "问题四\n连通性与重构\n特征差异指数评分\n不确定性补孔"),
    ]
    for x, _, text in boxes:
        rounded_box(ax, x - 1.08, 4.05, 2.16, 1.55, text, fs=9)
    arrow(ax, 5, 6.95, 5, 5.75)
    ax.text(1.45, 5.95, "候选掩膜 $M(x,y)$", fontsize=8.5, color=BLUE, ha="center")
    arrow(ax, 1.45, 5.72, 1.45, 5.66, color=BLUE)
    arrow(ax, 2.2, 5.35, 2.9, 5.35, color=BLUE)
    arrow(ax, 4.75, 5.35, 5.5, 5.35, color=BLUE)

    # 输出层
    outs = [
        (1.45, "同尺寸候选\n二值图\n平均覆盖 40.70%"),
        (3.85, "$R/P/\\beta/C$ 参数\n17 个候选簇\n最优 $R^2$=0.69"),
        (6.25, "$Z_2$/JRC 值\n44 组采样方案\n敏感性分析"),
        (8.55, "7 组连通评分\n补孔候选 3 处\n三维网络重构"),
    ]
    for x, text in outs:
        rounded_box(ax, x - 1.08, 2.35, 2.16, 1.15, text, fc="#E2EFDA", ec="#548235", fs=8.5)
        arrow(ax, x, 4.0, x, 3.55)

    rounded_box(ax, 2.3, 1.05, 5.4, 0.78, "四问结果汇编:结果表 · 图册 · 三维可视化 · 可复现代码",
                fc="#2F5597", ec="#1F3864", fs=10.5, bold=True, tc="#FFFFFF")
    for x in (1.45, 3.85, 6.25, 8.55):
        arrow(ax, x, 2.3, 5, 1.9)
    fig.savefig(OUT / "fig_route.png", dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(fig)


# ---------------------------------------------------------------- 问题一流程图
def fig_q1_flow() -> None:
    fig, ax = new_canvas(7.6, 8.6)
    steps = [
        ("开始", "se"),
        ("输入灰度图像 $I(x,y)$ (244×1350)", "p"),
        ("CLAHE 增强 (clip=2.0, 8×8 tile)", "p"),
        ("双边滤波 (d=7, σ=35) 抑制纹理噪声", "p"),
        ("黑帽变换 (15×15 椭圆核) 提取暗裂隙", "p"),
        ("Otsu 自适应阈值二值化", "p"),
        ("Canny 边缘 (35,110) 提取梯度结构", "p"),
        ("暗区 ∪ 边缘 并集融合", "p"),
        ("闭运算 → 开运算 (3×3)", "p"),
        ("8 邻域连通域, 面积 <12 px 剔除", "p"),
        ("输出同尺寸候选掩膜 $M(x,y)$", "o"),
        ("结束", "se"),
    ]
    n = len(steps)
    y0, dy = 9.4, 9.4 / n
    centers = []
    for i, (text, kind) in enumerate(steps):
        y = y0 - (i + 0.5) * dy
        if kind == "se":
            box = FancyBboxPatch((3.1, y - dy * 0.36), 1.8, dy * 0.72,
                                 boxstyle="round,pad=0.02,rounding_size=0.3",
                                 linewidth=1.3, edgecolor=BLUE, facecolor=BLUE)
            ax.add_patch(box)
            ax.text(4, y, text, ha="center", va="center", fontsize=10.5, color="white", fontweight="bold")
        elif kind == "o":
            rounded_box(ax, 2.2, y - dy * 0.36, 3.6, dy * 0.72, text, fc="#E2EFDA", ec="#548235", fs=9.5)
        else:
            rounded_box(ax, 1.45, y - dy * 0.36, 5.1, dy * 0.72, text, fs=9.5)
        centers.append(y)
    for i in range(n - 1):
        arrow(ax, 4, centers[i] - dy * 0.38, 4, centers[i + 1] + dy * 0.38)
    fig.savefig(OUT / "fig_q1_flow.png", dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(fig)


# ---------------------------------------------------------------- 问题二流程图
def fig_q2_flow() -> None:
    fig, ax = new_canvas(8.6, 7.4)
    rounded_box(ax, 3.5, 9.3, 2.2, 0.55, "开始", fc=BLUE, ec=BLUE, bold=True, tc="white")
    rounded_box(ax, 2.6, 8.25, 4.0, 0.62, "高斯平滑 (5×5) + Canny (35,110) 边缘检测", fs=9.5)
    rounded_box(ax, 2.6, 7.25, 4.0, 0.62, "边缘点降采样 (::6) 并归一化到 [0,1]²", fs=9.5)
    rounded_box(ax, 2.6, 6.25, 4.4, 0.62, "DBSCAN 聚类 (eps=0.055, min_samples=20)", fs=9.5)
    diamond(ax, 4.6, 5.15, 3.3, 1.0, "簇点数 ≥ 80 ?", fs=9.5)
    rounded_box(ax, 2.6, 3.85, 4.0, 0.62, "像素坐标 → mm 标定 (94.25 × 500)", fs=9.5)
    rounded_box(ax, 2.6, 2.85, 4.0, 0.62, "RANSAC 拟合 $y=a\\sin(\\omega x)+b\\cos(\\omega x)+C$\n(阈值 18 mm)", fs=9)
    rounded_box(ax, 2.6, 1.85, 4.0, 0.62, "参数恢复 $R=\\sqrt{a^2+b^2}$, $\\beta=\\mathrm{atan2}(b,a)$", fs=9.5)
    rounded_box(ax, 2.6, 0.85, 4.0, 0.62, "每图按 $R^2$ 保留前 3 个候选簇", fc="#E2EFDA", ec="#548235", fs=9.5)
    chain = [(4.6, 9.28, 4.6, 8.92), (4.6, 8.22, 4.6, 7.9), (4.6, 7.22, 4.6, 6.9),
             (4.6, 6.22, 4.6, 5.7), (4.6, 4.62, 4.6, 4.5), (4.6, 3.82, 4.6, 3.5),
             (4.6, 2.82, 4.6, 2.5), (4.6, 1.82, 4.6, 1.5)]
    for x1, y1, x2, y2 in chain:
        arrow(ax, x1, y1, x2, y2)
    ax.text(6.45, 5.15, "否(剔除)", fontsize=9, color=ORANGE)
    rounded_box(ax, 7.35, 4.9, 1.7, 0.55, "丢弃该簇", fc="#F2F2F2", ec=GRAY, fs=9)
    arrow(ax, 6.3, 5.15, 7.32, 5.15, color=ORANGE)
    ax.text(4.85, 5.62, "是", fontsize=9, color="#548235")
    rounded_box(ax, 0.4, 0.85, 1.7, 0.55, "结束", fc=BLUE, ec=BLUE, bold=True, tc="white")
    arrow(ax, 2.57, 1.16, 2.13, 1.16)
    fig.savefig(OUT / "fig_q2_flow.png", dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(fig)


# ---------------------------------------------------------------- 问题三流程图
def fig_q3_flow() -> None:
    fig, ax = new_canvas(7.6, 8.2)
    steps = [
        ("开始", "se"),
        ("输入附件3 复杂裂隙图像", "p"),
        ("高斯平滑 (7×7) + Canny (30,100)", "p"),
        ("轮廓检索 (RETR_LIST), 保留长度 ≥30 轮廓", "p"),
        ("取面积最大轮廓为候选裂隙轮廓", "p"),
        ("等间距采样 N=32/64/128 与\n曲率自适应采样 (64+高曲率加密)", "p"),
        ("同 x 坐标取纵坐标中位数, 消除零间距", "p"),
        ("像素坐标 → (x: 94.25 mm, y: 500 mm) 标定", "p"),
        ("计算 $Z_2$ (均方根斜率) → $\\mathrm{JRC}=51.85Z_2^{0.6}-10.37$", "o"),
        ("对比 4 种采样方案的 JRC 稳健性", "p"),
        ("结束", "se"),
    ]
    n = len(steps)
    y0, dy = 9.4, 9.4 / n
    centers = []
    for i, (text, kind) in enumerate(steps):
        y = y0 - (i + 0.5) * dy
        if kind == "se":
            box = FancyBboxPatch((3.1, y - dy * 0.33), 1.8, dy * 0.66,
                                 boxstyle="round,pad=0.02,rounding_size=0.3",
                                 linewidth=1.3, edgecolor=BLUE, facecolor=BLUE)
            ax.add_patch(box)
            ax.text(4, y, text, ha="center", va="center", fontsize=10.5, color="white", fontweight="bold")
        elif kind == "o":
            rounded_box(ax, 1.1, y - dy * 0.42, 5.8, dy * 0.84, text, fc="#E2EFDA", ec="#548235", fs=9.5)
        else:
            rounded_box(ax, 1.1, y - dy * 0.42, 5.8, dy * 0.84, text, fs=9.5)
        centers.append(y)
    for i in range(n - 1):
        arrow(ax, 4, centers[i] - dy * 0.46, 4, centers[i + 1] + dy * 0.46)
    fig.savefig(OUT / "fig_q3_flow.png", dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(fig)


# ---------------------------------------------------------------- 问题四流程图
def fig_q4_flow() -> None:
    fig, ax = new_canvas(8.6, 6.9)
    rounded_box(ax, 4.0, 9.35, 2.2, 0.55, "开始", fc=BLUE, ec=BLUE, bold=True, tc="white")
    rounded_box(ax, 2.7, 8.3, 4.8, 0.66, "六孔坐标布设 (1—6 号孔, 间距 1000 mm)", fs=9.5)
    rounded_box(ax, 2.7, 7.3, 4.8, 0.66, "40 段图像: 平滑 + Canny → 特征向量\n(边缘密度, 平均亮度, 竖直梯度)", fs=9)
    rounded_box(ax, 2.7, 6.3, 4.8, 0.66, "7 组相邻孔对 × 同深度段两两配对", fs=9.5)
    rounded_box(ax, 2.7, 5.3, 4.8, 0.66, "特征差异 $d=|\\Delta\\rho_{edge}|+0.002|\\Delta\\bar{I}|/255$", fs=9.5)
    rounded_box(ax, 2.7, 4.3, 4.8, 0.66, "相对连通评分 $p_{rel}=e^{-50d}$", fs=9.5)
    rounded_box(ax, 2.7, 3.3, 4.8, 0.66, "不确定性 $u=1-2|p_{rel}-0.5|$, 择小排序", fs=9.5)
    rounded_box(ax, 2.7, 2.3, 4.8, 0.66, "输出补孔候选前 3 处 (1-2 / 2-3 / 3-6)", fc="#E2EFDA", ec="#548235", fs=9.5)
    rounded_box(ax, 2.7, 1.3, 4.8, 0.66, "三维网络可视化 (孔迹 + 连通强度着色)", fs=9.5)
    rounded_box(ax, 4.0, 0.25, 2.2, 0.55, "结束", fc=BLUE, ec=BLUE, bold=True, tc="white")
    for y1, y2 in [(9.32, 9.0), (8.27, 7.99), (7.27, 6.99), (6.27, 5.99), (5.27, 4.99), (4.27, 3.99), (3.27, 2.99), (2.27, 1.99), (1.27, 0.83)]:
        arrow(ax, 5.1, y1, 5.1, y2)
    fig.savefig(OUT / "fig_q4_flow.png", dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(fig)


# ---------------------------------------------------------------- Q1 拼图与覆盖率
def fig_q1_montage() -> None:
    files = sorted(SRC_FIGS.glob("q1_图1-*_candidate.png"), key=lambda p: int(p.stem.split("图1-")[1].split("_")[0]))
    imgs = [Image.open(f) for f in files]
    gap = 14
    total_w = sum(im.width for im in imgs) + gap * (len(imgs) - 1)
    total_h = max(im.height for im in imgs) + 56
    canvas = Image.new("RGB", (total_w, total_h), "white")
    x = 0
    draw_labels = ["图1-%d" % i for i in range(1, 11)]
    from PIL import ImageDraw, ImageFont
    draw = ImageDraw.Draw(canvas)
    try:
        font = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 34)
    except OSError:
        font = ImageFont.load_default()
    for im, label in zip(imgs, draw_labels):
        canvas.paste(im, (x, 0))
        draw.text((x + im.width // 2 - 34, im.height + 8), label, fill="black", font=font)
        x += im.width + gap
    canvas.save(OUT / "fig_q1_montage.png")
    print("montage", canvas.size)


def fig_q1_coverage() -> None:
    rows = read_csv("q1_candidate_summary.csv")
    names = [r["image"].replace(".jpg", "") for r in rows]
    cov = [float(r["mask_coverage"]) * 100 for r in rows]
    order = sorted(range(len(names)), key=lambda i: int(names[i].split("-")[1]))
    names = [names[i] for i in order]
    cov = [cov[i] for i in order]
    fig, ax = plt.subplots(figsize=(8.6, 4.0))
    bars = ax.bar(names, cov, color=BLUE, width=0.62, edgecolor="white")
    mean = float(np.mean(cov))
    ax.axhline(mean, color=ORANGE, linestyle="--", linewidth=1.4)
    ax.text(9.35, mean + 1.2, f"均值 {mean:.2f}%", color=ORANGE, fontsize=10, ha="right")
    for b, v in zip(bars, cov):
        ax.text(b.get_x() + b.get_width() / 2, v + 0.8, f"{v:.1f}", ha="center", fontsize=8.6, color="#333333")
    ax.set_ylabel("候选掩膜覆盖率 / %")
    ax.set_xlabel("附件1 图像编号")
    ax.set_ylim(0, 70)
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis="y", linestyle=":", alpha=0.5)
    fig.tight_layout()
    fig.savefig(OUT / "fig_q1_coverage.png", dpi=200, facecolor="white")
    plt.close(fig)


# ---------------------------------------------------------------- Q2 图
def fig_q2_r2() -> None:
    rows = read_csv("q2_cluster_sine_results.csv")
    per_img: dict[str, list[float]] = {}
    for r in rows:
        per_img.setdefault(r["image"].replace(".jpg", ""), []).append(float(r["R2"]))
    keys = sorted(per_img, key=lambda k: int(k.split("-")[1].split(".")[0]))
    means = [float(np.mean(per_img[k])) for k in keys]
    fig, ax = plt.subplots(figsize=(8.6, 4.2))
    ax.bar(keys, means, color=BLUE, width=0.6, edgecolor="white", label="图像内均值")
    for k, x in zip(keys, range(len(keys))):
        ax.scatter([x] * len(per_img[k]), per_img[k], color=ORANGE, zorder=3, s=34, marker="D", label="候选簇" if x == 0 else None)
    overall = float(np.mean([float(r["R2"]) for r in rows]))
    ax.axhline(overall, color=GRAY, linestyle="--", linewidth=1.2)
    ax.text(len(keys) - 0.4, overall + 0.012, f"总体均值 {overall:.4f}", color=GRAY, fontsize=9.5, ha="right")
    best = max(float(r["R2"]) for r in rows)
    ax.annotate(f"最优簇 $R^2$={best:.3f}", xy=(7, best), xytext=(4.6, 0.63),
                arrowprops=dict(arrowstyle="->", color=TEAL), fontsize=10, color=TEAL)
    ax.set_ylabel("决定系数 $R^2$")
    ax.set_xlabel("附件2 图像编号")
    ax.set_ylim(0, 0.78)
    ax.legend(loc="upper left", frameon=False)
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis="y", linestyle=":", alpha=0.5)
    fig.tight_layout()
    fig.savefig(OUT / "fig_q2_r2.png", dpi=200, facecolor="white")
    plt.close(fig)


def fig_q2_sine() -> None:
    rows = read_csv("q2_cluster_sine_results.csv")
    rows.sort(key=lambda r: -float(r["R2"]))
    picks = rows[:6]
    fig, axes = plt.subplots(2, 3, figsize=(10.5, 5.6))
    x = np.linspace(0, 94.25, 400)
    for ax, r in zip(axes.ravel(), picks):
        R, beta, C = float(r["R_mm"]), float(r["beta_rad"]), float(r["C_mm"])
        y = R * np.sin(2 * math.pi * x / 94.25 + beta) + C
        ax.plot(x, y, color=BLUE, linewidth=2.0)
        ax.fill_between(x, y - float(r["RMSE_mm"]), y + float(r["RMSE_mm"]), color=BLUE, alpha=0.13,
                        label=f"±RMSE={float(r['RMSE_mm']):.1f} mm")
        ax.set_title(f"{r['image'].replace('.jpg','')} 簇{r['cluster']}  $R^2$={float(r['R2']):.3f}", fontsize=10)
        ax.set_xlabel("周向位置 / mm", fontsize=9)
        ax.set_ylabel("轴向位置 / mm", fontsize=9)
        ax.tick_params(labelsize=8.5)
        ax.legend(fontsize=8, frameon=False)
        ax.set_ylim(0, 620)
    fig.tight_layout()
    fig.savefig(OUT / "fig_q2_sine.png", dpi=200, facecolor="white")
    plt.close(fig)


# ---------------------------------------------------------------- Q3 图
def fig_q3_sens() -> None:
    rows = read_csv("q3_jrc_results.csv")
    per_img: dict[str, dict[str, list[tuple[float, float]]]] = {}
    for r in rows:
        img = r["image"].replace(".jpg", "")
        per_img.setdefault(img, {}).setdefault(r["method"], []).append(
            (int(r["sample_count"]), float(r["JRC"])))
    cmap = plt.get_cmap("viridis")
    fig, axes = plt.subplots(1, 2, figsize=(10.5, 4.2), gridspec_kw={"width_ratios": [2.1, 1]})
    ax = axes[0]
    imgs = sorted(per_img, key=lambda k: int(k.split("-")[1].split(".")[0]))
    for i, img in enumerate(imgs):
        uni = sorted(per_img[img].get("uniform", []))
        if uni:
            xs = [p[0] for p in uni]
            ys = [p[1] for p in uni]
            ax.plot(xs, ys, marker="o", markersize=4, linewidth=1.3,
                    color=cmap(i / max(len(imgs) - 1, 1)), label=img)
        for ad in per_img[img].get("curvature_adaptive", []):
            ax.scatter([ad[0]], [ad[1]], marker="*", s=90,
                       color=cmap(i / max(len(imgs) - 1, 1)), edgecolors="black", linewidths=0.4, zorder=5)
    ax.set_xlabel("等间距采样点数 N")
    ax.set_ylabel("JRC 基线值")
    ax.set_title("(a) 各图像 JRC 随采样密度的变化(星号为曲率自适应)", fontsize=10)
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(linestyle=":", alpha=0.5)
    ax2 = axes[1]
    data = []
    tick_labels = []
    for n in (32, 64, 128):
        vals = []
        for img in imgs:
            vals += [p[1] for p in per_img[img].get("uniform", []) if p[0] == n]
        if vals:
            data.append(vals)
            tick_labels.append(f"N={n}")
    adaptive = [p[1] for img in imgs for p in per_img[img].get("curvature_adaptive", [])]
    data.append(adaptive)
    tick_labels.append("曲率自适应")
    bp = ax2.boxplot(data, tick_labels=tick_labels, patch_artist=True)
    for patch in bp["boxes"]:
        patch.set_facecolor(LIGHT_BLUE)
        patch.set_edgecolor(BLUE)
    ax2.set_xlabel("采样方案")
    ax2.set_ylabel("JRC 基线值")
    ax2.set_title("(b) 采样方案间 JRC 分布对比", fontsize=10)
    ax2.spines[["top", "right"]].set_visible(False)
    ax2.grid(axis="y", linestyle=":", alpha=0.5)
    fig.tight_layout()
    fig.savefig(OUT / "fig_q3_sens.png", dpi=200, facecolor="white")
    plt.close(fig)


# ---------------------------------------------------------------- Q4 图
HOLES = {1: (500, 2000), 2: (1500, 2000), 3: (2500, 2000), 4: (500, 1000), 5: (1500, 1000), 6: (2500, 1000)}
NEIGHBORS = [(1, 2), (2, 3), (4, 5), (5, 6), (1, 4), (2, 5), (3, 6)]


def fig_q4_scores() -> None:
    rows = read_csv("q4_connectivity_results.csv")
    labels = [f"{r['hole_a']}-{r['hole_b']}" for r in rows]
    scores = [float(r["relative_score"]) for r in rows]
    unc = {r["between_holes"]: float(r["uncertainty_score"]) for r in read_csv("q4_uncertainty_candidates.csv")}
    fig, ax = plt.subplots(figsize=(8.6, 4.0))
    colors = [ORANGE if lab in unc else BLUE for lab in labels]
    bars = ax.bar(labels, scores, color=colors, width=0.6, edgecolor="white")
    for b, v in zip(bars, scores):
        ax.text(b.get_x() + b.get_width() / 2, v + 0.012, f"{v:.3f}", ha="center", fontsize=9)
    ax.set_ylabel("相对连通评分 $p_{rel}$")
    ax.set_xlabel("相邻钻孔对")
    ax.set_ylim(0.5, 1.0)
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis="y", linestyle=":", alpha=0.5)
    from matplotlib.patches import Patch
    ax.legend(handles=[Patch(fc=BLUE, label="常规相邻孔对"), Patch(fc=ORANGE, label="不确定性前 3(补孔候选)")],
              frameon=False, loc="lower right")
    fig.tight_layout()
    fig.savefig(OUT / "fig_q4_scores.png", dpi=200, facecolor="white")
    plt.close(fig)


def fig_q4_3d() -> None:
    rows = read_csv("q4_connectivity_results.csv")
    score_map = {(int(r["hole_a"]), int(r["hole_b"])): float(r["relative_score"]) for r in rows}
    fig = plt.figure(figsize=(9.2, 6.4))
    ax = fig.add_subplot(projection="3d")
    depth = 4000.0
    seg = 16
    for hid, (hx, hy) in HOLES.items():
        z = np.linspace(0, -depth, seg)
        ax.plot(np.full(seg, hx), np.full(seg, hy), z, color=BLUE, linewidth=2.6, alpha=0.85)
        ax.scatter([hx], [hy], [0], color="#1F3864", s=42, depthshade=False)
        ax.text(hx, hy, 160, f"{hid}#孔", fontsize=9.5, ha="center", color="#1F3864", fontweight="bold")
    for a, b in NEIGHBORS:
        s = score_map[(a, b)]
        (xa, ya), (xb, yb) = HOLES[a], HOLES[b]
        n = 24
        zz = np.linspace(-300, -depth + 300, n)
        bend = np.sin(np.linspace(0, math.pi, n)) * (1.0 - s) * 420.0
        t = np.linspace(0, 1, n)
        xs = xa + (xb - xa) * t
        ys = ya + (yb - ya) * t + bend
        ax.plot(xs, ys, zz, color=ORANGE if s < 0.8 else TEAL, linewidth=1.2 + 3.2 * s,
                alpha=0.55 + 0.4 * s)
        ax.text((xa + xb) / 2, (ya + yb) / 2 - 60, -depth * 0.55, f"{a}-{b}\n{s:.2f}",
                fontsize=8.2, ha="center", color="#333333")
    ax.set_xlabel("X / mm")
    ax.set_ylabel("Y / mm")
    ax.set_zlabel("孔深 / mm")
    ax.set_zlim(-depth, 500)
    ax.set_title("六钻孔空间布置与相邻孔对连通强度三维示意(线宽∝评分)", fontsize=11)
    ax.view_init(elev=28, azim=-58)
    fig.tight_layout()
    fig.savefig(OUT / "fig_q4_3d.png", dpi=200, facecolor="white")
    plt.close(fig)


if __name__ == "__main__":
    fig_route()
    fig_q1_flow()
    fig_q2_flow()
    fig_q3_flow()
    fig_q4_flow()
    fig_q1_montage()
    fig_q1_coverage()
    fig_q2_r2()
    fig_q2_sine()
    fig_q3_sens()
    fig_q4_scores()
    fig_q4_3d()
    print("PASS: paper figures ->", OUT)

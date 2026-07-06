# Re-running for the Day 30
import organoid_analyzer.organoid_analyzer as oa

SPACING_MU = (1 / 600) * 1e3  # 1 mm = 600 pixels


# oa.process_directory(
#     "../data/Organoid size of batch4/D30/P30",
#     "../processed/20260706/Organoid size of batch4/D30/P30",
#     threshold=0.93,
#     spacing=SPACING_MU,
#     cell_type="EB",
#     min_size=400,
# )

# oa.process_directory(
#     "../data/Organoid size of batch4/D30/R1868Q-11",
#     "../processed/20260706/Organoid size of batch4/D30/R1868Q-11",
#     threshold=0.93,
#     spacing=SPACING_MU,
#     cell_type="EB",
#     min_size=400,
# )

# oa.process_directory(
#     "../data/Organoid size of batch4/D30/R1868Q-20",
#     "../processed/20260706/Organoid size of batch4/D30/R1868Q-20",
#     threshold=0.93,
#     spacing=SPACING_MU,
#     cell_type="EB",
#     min_size=400,
# )

# oa.process_directory(
#     "../data/Organoid size of batch4/D30/R1868Q-28",
#     "../processed/20260706/Organoid size of batch4/D30/R1868Q-28",
#     threshold=0.93,
#     spacing=SPACING_MU,
#     cell_type="EB",
#     min_size=400,
# )

# oa.process_directory(
#     "../data/Organoid size of batch4/D30/R1868W-D11",
#     "../processed/20260706/Organoid size of batch4/D30/R1868W-D11",
#     threshold=0.93,
#     spacing=SPACING_MU,
#     cell_type="EB",
#     min_size=400,
# )

# oa.process_directory(
#     "../data/Organoid size of batch4/D30/R1868W-D39",
#     "../processed/20260706/Organoid size of batch4/D30/R1868W-D39",
#     threshold=0.93,
#     spacing=SPACING_MU,
#     cell_type="EB",
#     min_size=400,
# )

# oa.process_directory(
#     "../data/Organoid size of batch4/D30/WT-D26",
#     "../processed/20260706/Organoid size of batch4/D30/WT-D26",
#     threshold=0.93,
#     spacing=SPACING_MU,
#     cell_type="EB",
#     min_size=400,
# )

# ---

oa.process_directory(
    "../data/organoid size of new WT/D30/P29",
    "../processed/20260706/organoid size of new WT/D30/P29",
    threshold=0.93,
    spacing=SPACING_MU,
    cell_type="EB",
    min_size=400,
)

oa.process_directory(
    "../data/organoid size of new WT/D30/R1868Q-20",
    "../processed/20260706/organoid size of new WT/D30/R1868Q-20",
    threshold=0.93,
    spacing=SPACING_MU,
    cell_type="EB",
    min_size=400,
)

oa.process_directory(
    "../data/organoid size of new WT/D30/R1868Q-28",
    "../processed/20260706/organoid size of new WT/D30/R1868Q-28",
    threshold=0.93,
    spacing=SPACING_MU,
    cell_type="EB",
    min_size=400,
)

oa.process_directory(
    "../data/organoid size of new WT/D30/WT-D26",
    "../processed/20260706/organoid size of new WT/D30/WT-D26",
    threshold=0.93,
    spacing=SPACING_MU,
    cell_type="EB",
    min_size=400,
)


# image = skimage.io.imread(
#     r"D:\Projects\shi-lab-organoid-analysis\data\Organoid size of batch4\D30\P30\0008.tif"
# )

# mask = oa.segment_cells(image, threshold=0.95, min_size=350, debug_plot=True)

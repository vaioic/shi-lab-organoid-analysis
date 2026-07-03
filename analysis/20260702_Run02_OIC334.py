from shared import analyze_images

SPACING_MU = (1 / 600) * 1e3  # 1 mm = 600 pixels

analyze_images.process_timeseries_images(
    "../data/Organoid size of batch4",
    "../processed/20260703/Organoid size of batch4",
    threshold=0.9,
    spacing=SPACING_MU,
)

analyze_images.process_timeseries_images(
    "../data/organoid size of new WT",
    "../processed/20260703/organoid size of new WT",
    threshold=0.9,
    spacing=SPACING_MU,
)


# import organoid_analyzer.organoid_analyzer as oa

# # # oa.process_image(
# # #     "../data/Organoid size of batch4/D12/P30/0066.tif",
# # #     "../processed/20260703 Dev",
# # #     threshold=0.90,
# # #     spacing=(1 / 600) * 1e3,
# # #     cell_type="EB",
# # # )

# oa.process_directory(
#     "../data/Organoid size of batch4/D2/P30",
#     "../processed/20260703 Dev/Organoid size of batch4/D2/P30",
#     threshold=0.90,
#     spacing=(1 / 600) * 1e3,
#     cell_type="EB",
# )

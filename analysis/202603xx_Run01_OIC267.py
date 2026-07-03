from shared.analyze_images import process_images_in_dir

# process_images_in_dir('../data/20250927 real test batch1/D2', '../processed/2026-03-13/20250927 real test batch1/D2', include_subdirs=True, additional_coords={'Day': 2}, genotype_by="dir", spacing=(1000/594), threshold=0.95)

# process_images_in_dir('../data/20250927 real test batch1/D6', '../processed/2026-03-13/20250927 real test batch1/D6', include_subdirs=True, additional_coords={'Day': 6}, genotype_by="dir", spacing=(1000/594), threshold=0.95)

# process_images_in_dir('../data/20250927 real test batch1/D12', '../processed/2026-03-13/20250927 real test batch1/D12', include_subdirs=True, additional_coords={'Day': 12}, genotype_by="dir", spacing=(1000/594), threshold=1.0)

# process_images_in_dir('../data/20250927 real test batch1/D18', '../processed/2026-03-13/20250927 real test batch1/D18', include_subdirs=True, additional_coords={'Day': 18}, genotype_by="dir", spacing=(1000/594), threshold=1.0)

# process_images_in_dir('../data/20250927 real test batch1/D30', '../processed/2026-03-13/20250927 real test batch1/D30', include_subdirs=True, additional_coords={'Day': 30}, genotype_by="dir", spacing=(1000/594), threshold=1.0)

# ---

# process_images_in_dir('../data/20251205 real test batch2/D2', '../processed/2026-03-13/20251205 real test batch2/D2', include_subdirs=True, additional_coords={'Day': 2}, genotype_by="dir", spacing=(1000/594), threshold=0.95)

# process_images_in_dir('../data/20251205 real test batch2/D6', '../processed/2026-03-13/20251205 real test batch2/D6', include_subdirs=True, additional_coords={'Day': 6}, genotype_by="dir", spacing=(1000/594), threshold=0.95)

# process_images_in_dir('../data/20251205 real test batch2/D12', '../processed/2026-03-13/20251205 real test batch2/D12', include_subdirs=True, additional_coords={'Day': 12}, genotype_by="dir", spacing=(1000/594), threshold=1.0)

# process_images_in_dir('../data/20251205 real test batch2/D18', '../processed/2026-03-13/20251205 real test batch2/D18', include_subdirs=True, additional_coords={'Day': 18}, genotype_by="dir", spacing=(1000/594), threshold=1.0)

process_images_in_dir(
    "../data/20251205 real test batch2/D30",
    "../processed/2026-03-13/20251205 real test batch2/D30",
    include_subdirs=True,
    additional_coords={"Day": 30},
    genotype_by="dir",
    spacing=(1000 / 594),
    threshold=1.0,
)

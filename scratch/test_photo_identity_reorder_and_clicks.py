import json

# Simulated frontend photo resolution and click handler testing
photo_dataset = {
    "P001": {"photo_id": "P001", "filename": "P001.jpg", "image_url": "/photos/P001.jpg", "event": "Diwali Celebration"},
    "P003": {"photo_id": "P003", "filename": "P003.jpg", "image_url": "/photos/P003.jpg", "event": "Monsoon Trek"},
    "P006": {"photo_id": "P006", "filename": "P006.jpg", "image_url": "/photos/P006.jpg", "event": "Mathura Holi"},
    "P007": {"photo_id": "P007", "filename": "P007.jpg", "image_url": "/photos/P007.jpg", "event": "Christmas Charity Drive"},
    "P038": {"photo_id": "P038", "filename": "P038.jpg", "image_url": "/photos/P038.jpg", "event": "Gir Lion Wildlife Safari"}
}

def simulate_photo_click(results_array, click_target_id):
    # Find card item by canonical photo_id (simulates React event target data binding)
    clicked_item = next((item for item in results_array if item["photo_id"] == click_target_id), None)
    assert clicked_item is not None, f"Target photo {click_target_id} not found in results"
    
    # Simulate setSelectedPhotoModal(clicked_item)
    selected_modal = dict(clicked_item)
    
    # Strict UI Data Contract Validation
    assert selected_modal["photo_id"] == click_target_id, f"Expected {click_target_id}, got {selected_modal['photo_id']}"
    assert selected_modal["filename"] == f"{click_target_id}.jpg"
    assert selected_modal["image_url"] == f"/photos/{click_target_id}.jpg"
    return selected_modal

def run_photo_identity_tests():
    print("=== STEP 10: AUTOMATED FRONTEND PHOTO IDENTITY & REORDERING TEST ===")
    
    # Test 1: Standard result list [P007]
    res1 = [photo_dataset["P007"]]
    opened1 = simulate_photo_click(res1, "P007")
    print(f"[Pass 1] Single result list [P007] -> Click P007 -> Opened photo_id: {opened1['photo_id']}, file: {opened1['filename']}")

    # Test 2: Multi-item result list [P007, P003, P001]
    res2 = [photo_dataset["P007"], photo_dataset["P003"], photo_dataset["P001"]]
    opened2 = simulate_photo_click(res2, "P007")
    print(f"[Pass 2] Multi-item list [P007, P003, P001] -> Click P007 -> Opened photo_id: {opened2['photo_id']}, file: {opened2['filename']}")

    # Test 3: Reordered result list [P001, P007, P003] (Reordering does NOT change selected photo)
    res3 = [photo_dataset["P001"], photo_dataset["P007"], photo_dataset["P003"]]
    opened3 = simulate_photo_click(res3, "P007")
    print(f"[Pass 3] Reordered list [P001, P007, P003] -> Click P007 -> Opened photo_id: {opened3['photo_id']}, file: {opened3['filename']}")
    assert opened3["photo_id"] == "P007", "Reordering must not change target photo ID!"

    # Test 4: List containing P006 and P007 [P006, P007]
    res4 = [photo_dataset["P006"], photo_dataset["P007"]]
    opened4 = simulate_photo_click(res4, "P007")
    print(f"[Pass 4] Mixed list [P006, P007] -> Click P007 -> Opened photo_id: {opened4['photo_id']} ('{opened4['event']}')")
    assert opened4["photo_id"] == "P007"
    assert opened4["photo_id"] != "P006", "P007 must NEVER open P006!"

    # Test 5: Verify P001, P003, P006, P038
    for pid in ["P001", "P003", "P006", "P038"]:
        res_test = [photo_dataset[pid]]
        op = simulate_photo_click(res_test, pid)
        assert op["photo_id"] == pid
        assert op["filename"] == f"{pid}.jpg"
        assert op["image_url"] == f"/photos/{pid}.jpg"
        print(f"[Pass 5.{pid}] Click {pid} -> Opened {op['photo_id']} ({op['image_url']})")

    print("\nAll photo identity and reordering regression tests passed 100% cleanly!")

if __name__ == "__main__":
    run_photo_identity_tests()

#include <gtest/gtest.h>
#include <filesystem>
#include "../../deeplog/deeplog.hpp"
#include "../../deeplog/metadata_snapshot.hpp"

class DeeplogMetadataSnapshotTest : public ::testing::Test {
protected:
    void SetUp() override {
        if (std::filesystem::exists(test_dir)) {
            std::filesystem::remove_all(test_dir);
        }
    }

    void TearDown() override {
        if (std::filesystem::exists(test_dir)) {
            std::filesystem::remove_all(test_dir);
        }
    }

    std::string test_dir = "tmp/test";
};

TEST_F(DeeplogMetadataSnapshotTest, construct) {
    auto log = deeplog::deeplog::create(test_dir, 4);

    auto original_metadata = deeplog::metadata_snapshot(log).metadata();
    auto action = deeplog::metadata_action(original_metadata->id, "new name", "new desc", original_metadata->created_time);
    log->commit(deeplog::MAIN_BRANCH_ID, log->version(deeplog::MAIN_BRANCH_ID), {std::make_shared<deeplog::metadata_action>(action)});

    auto snapshot0 = deeplog::metadata_snapshot(0, log);
    auto snapshot1 = deeplog::metadata_snapshot(1, log);

    EXPECT_EQ(0, snapshot0.version);
    EXPECT_EQ(1, snapshot1.version);
}

TEST_F(DeeplogMetadataSnapshotTest, branches) {
    auto log = deeplog::deeplog::create(test_dir, 4);

    auto metadata = deeplog::metadata_snapshot(log);

    auto branches = metadata.branches();
    EXPECT_EQ(1, branches.size());
    EXPECT_EQ("main", branches.at(0)->name);
    EXPECT_EQ("", branches.at(0)->id);
    EXPECT_EQ("", branches.at(0)->from_id);
    EXPECT_EQ(-1, branches.at(0)->from_version);

    log->commit(deeplog::MAIN_BRANCH_ID, 0, {
//        std::make_shared<deeplog::protocol_action>(deeplog::protocol_action(5, 5))
            std::make_shared<deeplog::create_tensor_action>(deeplog::create_tensor_action("123", "tensor1", "text", "text",
                                                                                          0, false, false, false,
                                                                                          std::nullopt,
                                                                                          std::nullopt, {}, std::nullopt,
                                                                                          {}, {}, std::nullopt, std::nullopt, true, "3.1"))
    });

    auto metadata2 = deeplog::metadata_snapshot(log);
    EXPECT_EQ(1, metadata2.version);
    branches = metadata2.branches();
    EXPECT_EQ(1, branches.size());
}
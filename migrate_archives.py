#!/usr/bin/env python3
import os
import shutil
import logging
from pathlib import Path
from reset_game import update_runs_readme

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def ensure_dir_exists(directory):
    """Ensure a directory exists, create it if it doesn't."""
    if not os.path.exists(directory):
        os.makedirs(directory)
        logger.info(f"Created directory: {directory}")

def migrate_archives():
    """Migrate archives from the old location to the new location."""
    old_archive_dir = "archived_runs"
    new_archive_dir = "ai-dnd-test-vault/Runs/Archived"

    # Check if the old archive directory exists
    if not os.path.exists(old_archive_dir):
        logger.info(f"Old archive directory does not exist: {old_archive_dir}")
        return False

    # Ensure the new archive directory exists
    ensure_dir_exists(new_archive_dir)

    # Get list of archived runs in the old location
    migrated_count = 0
    for run_dir in os.listdir(old_archive_dir):
        old_run_path = os.path.join(old_archive_dir, run_dir)
        new_run_path = os.path.join(new_archive_dir, run_dir)

        if os.path.isdir(old_run_path):
            # Copy the archived run to the new location
            if os.path.exists(new_run_path):
                logger.warning(f"Run already exists in new location, skipping: {run_dir}")
                continue

            logger.info(f"Migrating run {run_dir} to new location...")
            shutil.copytree(old_run_path, new_run_path)
            migrated_count += 1

    logger.info(f"Migration complete. Migrated {migrated_count} archived runs.")

    # Optionally update the README to reflect the new archives
    if migrated_count > 0:
        try:
            update_runs_readme()
            logger.info("Updated Runs/README.md with migrated archives.")
        except Exception as e:
            logger.error(f"Failed to update Runs/README.md: {e}")

    return migrated_count > 0

def main():
    """Main function."""
    logger.info("Starting archive migration...")

    success = migrate_archives()

    if success:
        logger.info("Archive migration completed successfully!")

        # Ask if user wants to delete the old archives
        response = input("Do you want to delete the old archives? (y/n): ").strip().lower()
        if response == 'y':
            old_archive_dir = "archived_runs"
            shutil.rmtree(old_archive_dir)
            logger.info(f"Deleted old archive directory: {old_archive_dir}")
    else:
        logger.warning("No archives were migrated.")

if __name__ == "__main__":
    main()
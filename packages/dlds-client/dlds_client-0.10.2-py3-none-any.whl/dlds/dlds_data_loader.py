import os
import json
from collections import OrderedDict
from copy import copy
from typing import Dict, List, Optional
from enum import Enum

import numpy as np
from PIL import Image
from dlds import DLDSClient

# Constants
IMAGE_FILE_ENDINGS = ('.png', '.jpg', '.jpeg', '.bmp')
ANNOTATION_FILE_ENDING = '.json'


class LoadMode(Enum):
    PRELOAD = 0
    ADHOC = 1
    ADHOC_CACHED = 2


class DLDSDataLoader:
    """Data loader for data from the Data Spree Vision Platform"""

    def __init__(self, dlds_client: DLDSClient, network_model: Dict, mode: LoadMode, dataset_directory: str,
                 allowed_status=('annotated', 'reviewed')):
        """
        """
        self._dlds_client = dlds_client
        self._network_model = network_model
        self._dataset_directory = dataset_directory
        self._mode = mode
        self._allowed_status = allowed_status

        # load class label ids and names that are used within this model
        self._class_labels = dlds_client.get_model_class_labels(network_model['id'])

        self._subsets: Dict = {}

        if self._mode == LoadMode.PRELOAD:

            self.dataset_directories = {}
            for dataset_id in network_model['datasets']:
                dlds_client.download_dataset(os.path.join(dataset_directory, str(dataset_id)), dataset_id,
                                             accepted_status=allowed_status)
                self.dataset_directories[dataset_id] = {
                    'image_dir': os.path.join(dataset_directory, str(dataset_id), 'images'),
                    'annotation_dir': os.path.join(dataset_directory, str(dataset_id), 'annotations')
                }

                # for the moment, the subset_id is the same as the dataset_id
                subset_id = dataset_id
                self._subsets[subset_id] = {
                    'dataset_id': dataset_id
                }

        if self._mode == LoadMode.ADHOC:
            raise NotImplementedError

        if self._mode == LoadMode.ADHOC_CACHED:
            raise NotImplementedError

        # only used for creating categories
        train_split = network_model['parameters'].get('training_split', 0.8)

        self._items = {}
        self._item_ids = []
        self._item_subsets = []
        for dataset_id, data_dir in self.dataset_directories.items():
            image_files: List[str] = os.listdir(data_dir['image_dir'])
            image_files = list(filter(lambda f: f.lower().endswith(IMAGE_FILE_ENDINGS), image_files))

            label_files: List[str] = os.listdir(data_dir['annotation_dir'])
            label_files = list(filter(lambda f: f.endswith(ANNOTATION_FILE_ENDING), label_files))

            if len(label_files) > 0:
                for image_file in image_files:
                    # image file name without extension
                    base_name = os.path.splitext(image_file)[0]
                    item_id = int(base_name.split('_')[1])

                    # for the moment, the subset ID is the datset ID
                    subset_id = dataset_id

                    annotation_file = base_name + ANNOTATION_FILE_ENDING
                    if annotation_file in label_files:
                        self._item_ids.append(item_id)
                        self._item_subsets.append(subset_id)
                        self._items[item_id] = {
                            'dataset_id': dataset_id,
                            'image_file': image_file,
                            'annotation_file': annotation_file
                        }

        indices = np.arange(len(self._item_ids))
        if network_model['parameters']['dataset'].get('shuffle', True):
            np.random.seed(42)
            np.random.shuffle(indices)

        self._subsets_ids_by_category = OrderedDict()

        self._item_ids_by_category = {
            'train': [],
            'test': []
        }

        self._item_ids_by_subset = OrderedDict()

        for i, idx in enumerate(indices):
            item_id = self._item_ids[idx]

            category = 'train'
            if i >= train_split * len(self._items):
                category = 'test'

            self._item_ids_by_category[category].append(item_id)

            subset_id = self._item_subsets[idx]
            if subset_id not in self._item_ids_by_subset:
                self._item_ids_by_subset[subset_id] = []
            self._item_ids_by_subset[subset_id].append(item_id)

        for cat in self._item_ids_by_category:
            self._item_ids_by_category[cat] = list(set(self._item_ids_by_category[cat]))

    def get_class_labels(self) -> List[Dict]:
        """Get the list of class labels that are selected for the loaded model.

        :return: List containing the class labels with ID and name.
        """
        return copy(self._class_labels)

    def get_categories(self) -> List[str]:
        """List containing the names of all categories.

        :return: List of category names.
        """
        return list(self._item_ids_by_category.keys())

    def get_subset_ids(self, category=None) -> List[int]:
        """List containing the IDs of the subsets of the specified category or all subsets.

        :param category: Category to filter the subset IDs.
        :return: List of subset IDs.
        """

        if category is None:
            return list(self._item_ids_by_subset.keys())
        else:
            # TODO implement for specific categories
            raise NotImplemented

    def get_item_ids(self) -> List[int]:
        """List containing the IDs of all items.

        This list contains unique item IDs, e.g. an item that belongs to multiple subsets is only listed once.

        :return: List of item IDs.
        """
        return copy(list(set(self._item_ids)))

    def get_item_ids_by_category(self, category) -> List[int]:
        """Get the IDs of all items that belong to the specified category.

        :param category: Category to filter the item IDs.
        :return: List of item IDs.
        """
        return copy(self._item_ids_by_category.get(category, []))

    def get_item_ids_by_subset(self, subset_id):
        """Get the IDs of all items that belong to the specified subset.

        :param subset_id: ID of a subset.
        :return: List of item IDs.
        """
        return copy(self._item_ids_by_subset.get(subset_id, []))

    @staticmethod
    def default_load_image(image_path):
        image = Image.open(image_path)
        image = image.convert('RGB')
        return np.array(image)

    def get_item(self, item_id) -> Optional[Dict]:
        """Get dataset item given its ID.

        :param item_id: ID of the item.
        :param load_image:
        :return: Dictionary containing the image and meta data or None if the item does not exist.
        >>> {
        >>> 'id': int,
        >>> 'image': np.ndarray,
        >>> 'annotations': Dict
        >>> }
        """

        item = self._items.get(item_id)
        if item is None:
            return None

        dataset_id = item['dataset_id']
        image_file = item['image_file']
        annotation_file = item['annotation_file']

        image_path = os.path.join(self._dataset_directory, str(dataset_id), 'images', image_file)
        annotation_path = os.path.join(self._dataset_directory, str(dataset_id), 'annotations', annotation_file)

        # load image
        image = Image.open(image_path)
        image = image.convert('RGB')
        image = np.array(image)

        annotations = None
        with open(annotation_path) as f:
            annotations = json.load(f)
        if annotations is None:
            annotations = {}

        sample = {
            'id': item_id,
            'image': image,
            'annotations': annotations
        }

        return sample

from rest_framework import status

from zonesmart.product.models import BaseProduct, ProductImage
from zonesmart.product.tests import factories
from zonesmart.tests.base import BaseAPIViewTest, BaseViewSetTest


class BaseProductViewSetTest(BaseViewSetTest):
    url_path = "zonesmart:base_product:product"

    def get_base_product_list(self):
        url = self.get_url(postfix="list")
        return self.make_request(method="GET", url_path=url)

    def get_base_product(self, product_id):
        url = self.get_url(pk=product_id)
        return self.make_request(method="GET", url_path=url)

    def create_base_product(self, product):
        data = {
            "title": product.title,
            "description": product.description,
            "sku": product.sku,
            "value": product.value,
            "currency": product.currency,
        }
        url = self.get_url(postfix="list")
        return self.make_request(method="POST", url_path=url, data=data)

    def delete_base_product(self, product_id):
        url = self.get_url(pk=product_id)
        return self.make_request(method="DELETE", url_path=url)

    def update_base_product(self, product_id, data):
        url = self.get_url(pk=product_id)
        return self.make_request(method="PUT", url_path=url, data=data)

    def partial_update_base_product(self, product_id, data):
        url = self.get_url(pk=product_id)
        return self.make_request(method="PATCH", url_path=url, data=data)

    def upload_image(self, product_id, image, image_type):
        data = {
            "image_file": image.image_file.file,
            "description": image.description,
        }
        url = self.get_url(postfix="upload-image", pk=product_id, type=image_type)
        return self.make_request(
            method="POST", url_path=url, data=data, data_format="multipart"
        )

    def get_product_images(self, product_id):
        url = self.get_url(postfix="get-images", pk=product_id)
        return self.make_request(method="GET", url_path=url)

    def test_get_base_product_list(self):
        products = factories.BaseProductFactory.create_batch(size=3)
        response = self.get_base_product_list()
        self.assertStatus(response)
        self.assertEqual(response.json()["count"], len(products))

    def test_get_base_product(self):
        product = factories.BaseProductFactory.create()
        response = self.get_base_product(product_id=product.id)
        self.assertStatus(response)
        self.assertEqual(response.json()["title"], product.title)

    def test_create_base_product(self):
        product = factories.BaseProductFactory.build()
        response = self.create_base_product(product)
        self.assertStatus(response, status=status.HTTP_201_CREATED)
        self.assertEqual(BaseProduct.objects.filter(title=product.title).count(), 1)

    def test_delete_base_product(self):
        product = factories.BaseProductFactory.create()
        response = self.delete_base_product(product_id=product.id)
        self.assertStatus(response, status=status.HTTP_204_NO_CONTENT)
        self.assertEqual(BaseProduct.objects.filter(id=product.id).count(), 0)

    def test_update_base_product(self):
        product = factories.BaseProductFactory.create(
            title="to be the same",
            description="to be updated",
            converted_from_currency="to be deleted",
        )
        self.assertIsNotNone(product.title)
        self.assertIsNotNone(product.description)
        self.assertIsNotNone(product.converted_from_currency)

        wrong_data = {
            "description": "updated description",
        }
        with self.assertRaisesMessage(AssertionError, "400 != 200"):
            response = self.update_base_product(product_id=product.id, data=wrong_data)
            self.assertStatus(response)

        right_data = {
            "title": product.title,
            "description": "updated description",
            "sku": product.sku,
            "value": product.value,
            "currency": product.currency,
            "converted_from_currency": None,
        }
        response = self.update_base_product(product_id=product.id, data=right_data)
        self.assertStatus(response)
        updated_product = BaseProduct.objects.get(id=product.id)
        self.assertEqual(updated_product.title, product.title)
        self.assertIsNotNone(updated_product.description)
        self.assertNotEqual(updated_product.description, product.description)
        self.assertIsNone(updated_product.converted_from_currency)

    def test_partial_update_base_product(self):
        product = factories.BaseProductFactory.create(
            title="to be the same",
            description="to be updated",
            converted_from_currency="to be deleted",
        )
        self.assertIsNotNone(product.title)
        self.assertIsNotNone(product.description)
        self.assertIsNotNone(product.converted_from_currency)

        data = {
            "title": product.title,
            "description": "updated description",
            "converted_from_currency": None,
        }
        response = self.partial_update_base_product(product_id=product.id, data=data)
        self.assertStatus(response)
        updated_product = BaseProduct.objects.get(id=product.id)
        self.assertEqual(updated_product.title, product.title)
        self.assertIsNotNone(updated_product.description)
        self.assertNotEqual(updated_product.description, product.description)
        self.assertIsNone(updated_product.converted_from_currency)

    def test_upload_product_main_image(self):
        product = factories.BaseProductFactory.create(main_image=None)

        image = factories.ProductImageFactory.build()
        response = self.upload_image(
            product_id=product.id, image=image, image_type="main",
        )
        self.assertStatus(response, status=status.HTTP_201_CREATED)
        self.assertEqual(
            ProductImage.objects.filter(description=image.description).count(), 1
        )
        self.assertIsNotNone(
            BaseProduct.objects.get(id=product.id).main_image.image_file.url
        )
        self.assertEqual(
            BaseProduct.objects.get(id=product.id).main_image.id,
            ProductImage.objects.get(description=image.description).id,
        )

    def test_upload_product_extra_image(self):
        BaseProduct.objects.all().delete()
        ProductImage.objects.all().delete()

        product = factories.BaseProductFactory.create(main_image=None)

        images = factories.ProductImageFactory.build_batch(size=3)
        for image in images:
            response = self.upload_image(
                product_id=product.id, image=image, image_type="extra",
            )
            self.assertStatus(response, status=status.HTTP_201_CREATED)

        images_ids = [image.id for image in ProductImage.objects.all()]
        self.assertEqual(len(images_ids), len(images))

        product = BaseProduct.objects.get(id=product.id)
        self.assertEqual(len(product.extra_images.all()), len(images))

        for image in product.extra_images.all():
            self.assertIn(image.id, images_ids)

    def test_get_product_images(self):
        images = factories.ProductImageFactory.create_batch(size=3)
        product = factories.BaseProductFactory.create(extra_images=images)

        response = self.get_product_images(product_id=product.id)
        self.assertStatus(response)
        self.assertEqual(
            product.main_image.image_file.url, response.json()["main_image"]
        )

        for image in product.extra_images.all():
            self.assertIn(image.image_file.url, response.json()["extra_images"])


class BaseProductImagesTest(BaseAPIViewTest):
    url_path = "zonesmart:base_product:images"

    def get_product_image(self, image_id):
        url = self.get_url(id=image_id)
        return self.make_request(method="GET", url_path=url)

    def delete_product_image(self, image_id):
        url = self.get_url(id=image_id)
        return self.make_request(method="DELETE", url_path=url)

    def test_get_product_image(self):
        image = factories.ProductImageFactory.create()
        response = self.get_product_image(image_id=image.id)
        self.assertStatus(response)
        self.assertEqual(str(image.id), response.json()["id"])
        self.assertEqual(image.image_file.url, response.json()["url"])

    def test_delete_product_image(self):
        image = factories.ProductImageFactory.create()
        response = self.delete_product_image(image_id=image.id)
        self.assertStatus(response, status=status.HTTP_204_NO_CONTENT)
        self.assertEqual(ProductImage.objects.filter(id=image.id).count(), 0)

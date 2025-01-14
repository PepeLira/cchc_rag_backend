import logging
from openai import OpenAI
import base64
import io
from PIL import Image
import tiktoken

_log = logging.getLogger(__name__)

class OpenAIVisionClient:

    def __init__(self, api_key: str, model: str = "gpt-4o"):
        self.client = OpenAI( api_key= api_key)
        self.model = model

    def describe_image(self, image_path: str) -> str:
        try:
            # Encode the image to base64
            base64_image = self._encode_image_to_base64_within_token_limit(
                image_path,
                model=self.model
            )

            # Create the message payload
            messages = [
                {
                    "role": "user",
                    "content": f"![image](data:image/jpeg;base64,{base64_image})\nDescribe the content of this image."
                }
            ]

            # Send the request to the OpenAI API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=300
            )

            # Extract and return the description from the response
            description = response.choices[0].message.content
            _log.info(f"La siguiente imagen se puede decribir como: {description}")
            return description

        except Exception as e:
            _log.error(f"Error during image description: {e}")
            raise

    def _encode_image_to_base64_within_token_limit(
        self,
        image_path: str,
        token_limit: int = 25000,
        model: str = "gpt-4o",
        quality_step: int = 10,
        resize_step: float = 0.9
    ) -> str:

        # Load the image once
        with Image.open(image_path) as img:
            # We'll start with a moderate JPEG quality
            quality = 85

            while True:
                # 1) Compress (save) to an in-memory buffer with current quality
                buffer = io.BytesIO()
                img.save(buffer, format="JPEG", quality=quality)
                buffer.seek(0)

                # 2) Convert to base64
                base64_image = base64.b64encode(buffer.read()).decode("utf-8")

                # 3) Build a minimal prompt with the base64-encoded image
                content = (
                    f"![image](data:image/jpeg;base64,{base64_image})\n"
                    "Describe the content of this image."
                )

                # 4) Count tokens
                encoding = tiktoken.encoding_for_model(model)
                token_count = len(encoding.encode(content))

                # 5) Check if we are within the limit
                if token_count <= token_limit:
                    print(f"[INFO] Final prompt size: {token_count} tokens.")
                    return base64_image

                # Otherwise, compress more
                print(
                    f"[INFO] Current token count {token_count} exceeds {token_limit}. "
                    f"Trying to reduce size (quality={quality}, size={img.size})."
                )

                # Lower the JPEG quality
                new_quality = quality - quality_step
                if new_quality < 10:
                    # If reducing quality alone isn't enough, start resizing
                    new_width = int(img.width * resize_step)
                    new_height = int(img.height * resize_step)
                    # If the image is already very small, bail out
                    if new_width < 10 or new_height < 10:
                        raise ValueError(
                            f"Unable to compress the image enough to fit within {token_limit} tokens."
                        )
                    img = img.resize((new_width, new_height))
                    # Reset quality to a moderate range again to see if resizing helps
                    quality = 85
                else:
                    # Just reduce quality further
                    quality = new_quality
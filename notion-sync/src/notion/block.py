from typing import Dict, Any, List

class BlockConverter:
    @staticmethod
    def to_markdown(block: Dict[str, Any]) -> str:
        """NotionブロックをMarkdownに変換"""
        block_type = block.get("type")
        if not block_type:
            return ""

        converter = getattr(BlockConverter, f"convert_{block_type}", None)
        if converter:
            return converter(block)
        return ""

    @staticmethod
    def convert_paragraph(block: Dict[str, Any]) -> str:
        """段落ブロックを変換"""
        text = "".join(
            span.get("plain_text", "")
            for span in block["paragraph"]["rich_text"]
        )
        return f"{text}\n\n"

    @staticmethod
    def convert_heading_1(block: Dict[str, Any]) -> str:
        """見出し1を変換"""
        text = "".join(
            span.get("plain_text", "")
            for span in block["heading_1"]["rich_text"]
        )
        return f"# {text}\n\n"

    @staticmethod
    def convert_heading_2(block: Dict[str, Any]) -> str:
        """見出し2を変換"""
        text = "".join(
            span.get("plain_text", "")
            for span in block["heading_2"]["rich_text"]
        )
        return f"## {text}\n\n"

    @staticmethod
    def convert_heading_3(block: Dict[str, Any]) -> str:
        """見出し3を変換"""
        text = "".join(
            span.get("plain_text", "")
            for span in block["heading_3"]["rich_text"]
        )
        return f"### {text}\n\n"

    @staticmethod
    def convert_bulleted_list_item(block: Dict[str, Any]) -> str:
        """箇条書きリストを変換"""
        text = "".join(
            span.get("plain_text", "")
            for span in block["bulleted_list_item"]["rich_text"]
        )
        return f"- {text}\n"

    @staticmethod
    def convert_numbered_list_item(block: Dict[str, Any]) -> str:
        """番号付きリストを変換"""
        text = "".join(
            span.get("plain_text", "")
            for span in block["numbered_list_item"]["rich_text"]
        )
        return f"1. {text}\n"

    @staticmethod
    def convert_code(block: Dict[str, Any]) -> str:
        """コードブロックを変換"""
        text = "".join(
            span.get("plain_text", "")
            for span in block["code"]["rich_text"]
        )
        language = block["code"]["language"]
        return f"```{language}\n{text}\n```\n\n"

    @staticmethod
    def convert_image(block: Dict[str, Any]) -> str:
        """画像ブロックを変換"""
        caption = "".join(
            span.get("plain_text", "")
            for span in block["image"]["caption"]
        )
        url = block["image"]["file"]["url"]
        return f"![{caption}]({url})\n\n"

    @staticmethod
    def convert_child_page(block: Dict[str, Any]) -> str:
        """子ページブロックを変換"""
        title = block["child_page"]["title"]
        return f"## {title}\n\n"

    @staticmethod
    def blocks_to_markdown(blocks: List[Dict[str, Any]]) -> str:
        """複数のブロックをMarkdownに変換"""
        return "".join(BlockConverter.to_markdown(block) for block in blocks) 
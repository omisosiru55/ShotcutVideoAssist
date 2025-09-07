from lxml import etree

class Project:
    def __init__(self, profile="hdv_720_25p"):
        self.root = etree.Element("mlt")
        self.profile = profile
        etree.SubElement(self.root, "profile", name=profile)

        # main playlist
        self.playlist = etree.SubElement(self.root, "playlist", id="main")

    def add_producer(self, src, in_point="0", out_point=None):
        """動画ファイルなどの素材を追加"""
        producer_id = f"producer{len(self.root.findall('producer'))+1}"
        producer = etree.SubElement(self.root, "producer", id=producer_id)
        etree.SubElement(producer, "property", name="resource").text = src
        if out_point:
            etree.SubElement(producer, "property", name="out").text = str(out_point)

        # playlist に追加
        entry = etree.SubElement(self.playlist, "entry", producer=producer_id, in_=str(in_point))
        return producer_id

    def add_filter(self, producer_id, filter_name, **params):
        """フィルタを追加"""
        filt = etree.SubElement(self.root, "filter")
        etree.SubElement(filt, "property", name="mlt_service").text = filter_name
        etree.SubElement(filt, "property", name="producer").text = producer_id
        for k, v in params.items():
            etree.SubElement(filt, "property", name=k).text = str(v)

    def to_xml(self, pretty_print=True):
        return etree.tostring(self.root, pretty_print=pretty_print, encoding="utf-8").decode("utf-8")

    def save(self, path):
        with open(path, "w", encoding="utf-8") as f:
            f.write(self.to_xml())

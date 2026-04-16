"""Academic publication records."""
from django.db import models
from django.utils.translation import gettext_lazy as _


class Publication(models.Model):
    title = models.TextField(_("Başlık"))
    authors = models.CharField(
        _("Yazarlar"),
        max_length=500,
        help_text=_("Örn: Takmaz O, Bastu E, Ozbasli E, Gundogan S, ..."),
    )
    journal = models.CharField(_("Dergi"), max_length=240)
    year = models.PositiveIntegerField(_("Yıl"))
    volume = models.CharField(_("Cilt"), max_length=40, blank=True)
    issue = models.CharField(_("Sayı"), max_length=40, blank=True)
    pages = models.CharField(_("Sayfa Aralığı"), max_length=60, blank=True)
    doi = models.CharField(_("DOI"), max_length=120, blank=True)
    pubmed_id = models.CharField(_("PubMed ID"), max_length=40, blank=True)
    pmc_id = models.CharField(_("PMC ID"), max_length=40, blank=True)
    citation_count = models.PositiveIntegerField(_("Atıf Sayısı"), default=0)
    abstract = models.TextField(_("Özet"), blank=True)
    full_url = models.URLField(_("Tam Metin URL"), blank=True)
    is_featured = models.BooleanField(_("Öne Çıkan"), default=False)
    order = models.PositiveIntegerField(_("Sıra"), default=0)

    class Meta:
        ordering = ["-year", "-citation_count", "order"]
        verbose_name = _("Yayın")
        verbose_name_plural = _("Yayınlar")

    def __str__(self):
        return f"{self.title[:60]}… ({self.year})"

    @property
    def apa_citation(self) -> str:
        parts = [self.authors.rstrip(".") + "."] if self.authors else []
        parts.append(f"({self.year}).")
        parts.append(self.title.rstrip(".") + ".")
        journal = f"<em>{self.journal}</em>"
        if self.volume:
            vol = self.volume
            if self.issue:
                vol += f"({self.issue})"
            journal += f", {vol}"
        if self.pages:
            journal += f", {self.pages}"
        parts.append(journal + ".")
        if self.doi:
            parts.append(f"https://doi.org/{self.doi}")
        return " ".join(parts)

    @property
    def pubmed_url(self) -> str:
        if self.pubmed_id:
            return f"https://pubmed.ncbi.nlm.nih.gov/{self.pubmed_id}/"
        return ""

    @property
    def best_url(self) -> str:
        """First working link for the card click-through."""
        from urllib.parse import quote
        if self.full_url:
            return self.full_url
        if self.pubmed_id:
            return f"https://pubmed.ncbi.nlm.nih.gov/{self.pubmed_id}/"
        if self.doi:
            return f"https://doi.org/{self.doi}"
        return f"https://scholar.google.com/scholar?q={quote(self.title)}"

from janis_core import File


class FastaFai(File):
    def __init__(self, optional=False):
        super().__init__(optional=optional, extension=".fasta")

    @staticmethod
    def name():
        return "FastaFai"

    @staticmethod
    def secondary_files():
        return [".fai"]


class Fasta(FastaFai):
    @staticmethod
    def name():
        return "Fasta"

    @staticmethod
    def secondary_files():
        return [".amb", ".ann", ".bwt", ".pac", ".sa", *FastaFai.secondary_files()]


class FastaWithDict(Fasta):
    @staticmethod
    def name():
        return "FastaWithDict"

    @staticmethod
    def secondary_files():
        # [".fai", ".amb", ".ann", ".bwt", ".pac", ".sa", "^.dict"]
        return [*Fasta.secondary_files(), "^.dict"]

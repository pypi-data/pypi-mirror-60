# # Building transaction
# def build_transaction(self, inputs: list, outputs: list, locktime=0, **kwargs):
#     # Building mutable bitcoin transaction
#     self.transaction = MutableTransaction(version=self.version, ins=inputs,
#                                           outs=outputs, locktime=Locktime(locktime))
#     return self
#
# # Signing transaction
# def sign(self, outputs: list, solver: list):
#     self.transaction.spend(outputs, solver)
#     return self

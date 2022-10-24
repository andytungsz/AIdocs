import onnx

onnx_model = onnx.load("srcnn.onnx")

try:
    onnx.checker.check_model(onnx_model)
except Exception:
    print(" model incorrect")
else:
    print(" model correct")


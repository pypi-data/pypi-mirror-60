FOLDER=$1

echo importing ( creating shared object ): nvcc -lcublas -lcufft -lcusolver -O3 --compiler-options '-fPIC' -shared CUDA\ C\ ++\ sources -o cuGMRES.so
nvcc -lcublas -lcufft -lcusolver -O3 --compiler-options '-fPIC' -shared ${FOLDER}/CUDA\ C\ ++\ sources/GMRES.cu -o ${FOLDER}/Shared\ object\ generating/cuGMRES.so


from PIL import Image
import matplotlib.pyplot as plt

def launch_doc_calibrator(image_path: str):

    img = Image.open(image_path)
    fig, ax = plt.subplots(figsize=(12,16))

    ax.imshow(img)
    coord = []

    def onclick(event):
        if event.xdata and event.ydata:

            coord.append((int(event.xdata), int(event.ydata)))
            ax.plot(event.xdata, event.ydata, 'r+', markersize=10)
            fig.canvas.draw()

            print(f"Point {len(coord)}: ({int(event.xdata)}, {int(event.ydata)})")
    
    fig.canvas.mpl_connect('button_press_event', onclick)
    plt.title("Click: top-left corner, then bottom-right corner of each zone")
    plt.show()
    return coord


if __name__ == "__main__":
    path = r'E:\npd-master-data-poc\vlm_extractor\vlm_docs_samples\test3.png'
    points = launch_doc_calibrator(path)
    img = Image.open(path)
    print(img.size)
    print("\nAll points:", points)
import os
from flask import Flask, render_template, redirect, url_for, flash, request, send_from_directory
from flask_bootstrap import Bootstrap5
import datetime
from flask_wtf import FlaskForm
from werkzeug.utils import secure_filename
from flask_wtf.file import FileField
import numpy as np
from PIL import Image
from sklearn.cluster import KMeans
from collections import Counter

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('FLASK_KEY')
Bootstrap5(app)

x = datetime.datetime.now()

app.config['UPLOAD_FOLDER'] = 'static/images'


class UploadForm(FlaskForm):
    image = FileField('image')


@app.route('/',  methods=['GET', 'POST'])
def main_page():
    form = UploadForm()
    if form.validate_on_submit():
        image = form.image.data
        filename = secure_filename(image.filename)
        image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        img = Image.open(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        image_data = np.array(img)
        # reshape 3D array to 2D array
        # -1 means unknown number of rows, 3 means there's 3 columns (RGB)
        image_data = image_data.reshape(-1, 3)
        kmeans = KMeans(n_clusters=3)
        kmeans.fit(image_data)
        color_cluster = kmeans.cluster_centers_.tolist()
        colors = color_cluster
        occurrences = Counter(kmeans.labels_)
        color_palette = []
        for rgb_list in colors:
            new_colors = [int(value) for value in rgb_list]
            color_palette.append(new_colors)
        color_percentages = {i: occurrences[i] / len(image_data) * 100 for i in occurrences}
        return render_template("index.html", date=x.year, form=form, upload=True, filename=filename,
                               color_percentages=color_percentages, colors=color_palette)

    return render_template("index.html", date=x.year, form=form)


@app.route('/images/<filename>')
def serve_image(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True, upload=True)


if __name__ == "__main__":
    app.run(debug=False, port=5001, )

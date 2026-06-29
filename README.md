# Edit README.md dan ganti semua 'yourusername' dengan username GitHub Anda
sed -i 's/CPA0711/g' README.md

# Commit perubahan
git add README.md
git commit -m "Update badge with correct username"
git push

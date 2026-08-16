using System.Drawing.Drawing2D;

namespace ImageViewerWinForms;

public partial class Form1 : Form
{
    private readonly ImageCanvas _imageCanvas = new();
    private readonly Label _fileValueLabel = CreateValueLabel();
    private readonly Label _widthValueLabel = CreateValueLabel();
    private readonly Label _heightValueLabel = CreateValueLabel();
    private readonly Label _pixelsValueLabel = CreateValueLabel();
    private readonly Label _xValueLabel = CreateValueLabel();
    private readonly Label _yValueLabel = CreateValueLabel();
    private readonly Label _zoomValueLabel = CreateValueLabel("100%");
    private readonly ToolStripStatusLabel _statusLabel = new("이미지를 열어 주세요.");
    private readonly TrackBar _zoomTrackBar = new();

    private Bitmap? _currentBitmap;
    private string _currentFilePath = string.Empty;
    private double _resolutionX = 50.0;
    private double _resolutionY = 30.0;

    public Form1()
    {
        InitializeComponent();
        BuildLayout();
        WireEvents();
        FormClosed += (_, _) => _currentBitmap?.Dispose();
    }

    private void BuildLayout()
    {
        Text = "C# WinForms 이미지 뷰어";
        StartPosition = FormStartPosition.CenterScreen;
        MinimumSize = new Size(1100, 700);
        ClientSize = new Size(1368, 720);

        var statusStrip = new StatusStrip();
        statusStrip.Items.Add(_statusLabel);

        var rightPanel = new TableLayoutPanel
        {
            Dock = DockStyle.Right,
            Width = 280,
            Padding = new Padding(12),
            ColumnCount = 1,
            RowCount = 5
        };

        rightPanel.RowStyles.Add(new RowStyle(SizeType.AutoSize));
        rightPanel.RowStyles.Add(new RowStyle(SizeType.AutoSize));
        rightPanel.RowStyles.Add(new RowStyle(SizeType.AutoSize));
        rightPanel.RowStyles.Add(new RowStyle(SizeType.AutoSize));
        rightPanel.RowStyles.Add(new RowStyle(SizeType.Percent, 100));

        var openButton = CreateButton("이미지 열기");
        var judgeButton = CreateButton("검사 준비 확인");
        var resolutionButton = CreateButton("분해능 설정");
        var measureButton = CreateButton("거리 측정");
        var clearMeasureButton = CreateButton("측정선 지우기");

        var actionPanel = new FlowLayoutPanel
        {
            Dock = DockStyle.Fill,
            AutoSize = true,
            FlowDirection = FlowDirection.TopDown,
            WrapContents = false
        };

        actionPanel.Controls.Add(openButton);
        actionPanel.Controls.Add(judgeButton);
        actionPanel.Controls.Add(resolutionButton);
        actionPanel.Controls.Add(measureButton);
        actionPanel.Controls.Add(clearMeasureButton);

        _zoomTrackBar.Minimum = 50;
        _zoomTrackBar.Maximum = 400;
        _zoomTrackBar.TickFrequency = 50;
        _zoomTrackBar.Value = 100;
        _zoomTrackBar.Dock = DockStyle.Top;

        var zoomGroup = new GroupBox
        {
            Text = "Zoom",
            Dock = DockStyle.Top,
            AutoSize = true,
            Padding = new Padding(12)
        };

        var zoomPanel = new TableLayoutPanel
        {
            Dock = DockStyle.Top,
            AutoSize = true,
            ColumnCount = 1
        };

        zoomPanel.Controls.Add(_zoomTrackBar);
        zoomPanel.Controls.Add(_zoomValueLabel);
        zoomGroup.Controls.Add(zoomPanel);

        rightPanel.Controls.Add(CreateInfoGroup("Image Information", new[]
        {
            ("File", _fileValueLabel),
            ("Width", _widthValueLabel),
            ("Height", _heightValueLabel),
            ("Pixels", _pixelsValueLabel)
        }));

        rightPanel.Controls.Add(CreateInfoGroup("Pixel Information", new[]
        {
            ("X", _xValueLabel),
            ("Y", _yValueLabel)
        }));

        rightPanel.Controls.Add(zoomGroup);
        rightPanel.Controls.Add(actionPanel);

        var imageHost = new Panel
        {
            Dock = DockStyle.Fill,
            Padding = new Padding(12),
            BackColor = Color.FromArgb(45, 45, 48)
        };

        imageHost.Controls.Add(_imageCanvas);

        Controls.Add(imageHost);
        Controls.Add(rightPanel);
        Controls.Add(statusStrip);

        openButton.Click += (_, _) => OpenImage();
        judgeButton.Click += (_, _) => CheckReady();
        resolutionButton.Click += (_, _) => OpenResolutionDialog();
        measureButton.Click += (_, _) => StartMeasureMode();
        clearMeasureButton.Click += (_, _) => ClearMeasurements();
    }

    private void WireEvents()
    {
        _zoomTrackBar.ValueChanged += (_, _) =>
        {
            var zoom = _zoomTrackBar.Value / 100f;
            _imageCanvas.Zoom = zoom;
            _zoomValueLabel.Text = $"{_zoomTrackBar.Value}%";
            _statusLabel.Text = $"Zoom : {_zoomTrackBar.Value}%";
        };

        _imageCanvas.PixelHovered += (_, point) =>
        {
            if (point is null)
            {
                _xValueLabel.Text = "-";
                _yValueLabel.Text = "-";
                return;
            }

            _xValueLabel.Text = point.Value.X.ToString();
            _yValueLabel.Text = point.Value.Y.ToString();
        };

        _imageCanvas.MeasurementCompleted += (_, distance) =>
        {
            _statusLabel.Text = $"거리 측정 완료 : {distance:F2} um";
        };
    }

    private void OpenImage()
    {
        using var dialog = new OpenFileDialog
        {
            Title = "검사할 이미지 선택",
            Filter = "Bitmap Image (*.bmp)|*.bmp|Image Files (*.bmp;*.png;*.jpg;*.jpeg)|*.bmp;*.png;*.jpg;*.jpeg"
        };

        if (dialog.ShowDialog(this) != DialogResult.OK)
        {
            return;
        }

        try
        {
            // 파일 잠금을 피하기 위해 원본 스트림에서 복사본 Bitmap을 만든다.
            using var loaded = new Bitmap(dialog.FileName);
            var bitmapCopy = new Bitmap(loaded);

            _currentBitmap?.Dispose();
            _currentBitmap = bitmapCopy;
            _currentFilePath = dialog.FileName;

            _imageCanvas.SetImage(_currentBitmap);
            _zoomTrackBar.Value = 100;
            UpdateImageInfo();
            _statusLabel.Text = $"Loaded : {Path.GetFileName(dialog.FileName)} ({_currentBitmap.Width} x {_currentBitmap.Height})";
        }
        catch (Exception ex)
        {
            MessageBox.Show(this, $"이미지를 불러오지 못했습니다.{Environment.NewLine}{ex.Message}", "이미지 로딩 실패",
                MessageBoxButtons.OK, MessageBoxIcon.Error);
            _statusLabel.Text = "이미지 로딩 실패";
        }
    }

    private void CheckReady()
    {
        if (_currentBitmap is null || _currentBitmap.Width == 0 || _currentBitmap.Height == 0)
        {
            MessageBox.Show(this, "이미지를 먼저 열어 주세요.", "확인", MessageBoxButtons.OK, MessageBoxIcon.Information);
            return;
        }

        if (!File.Exists(_currentFilePath))
        {
            MessageBox.Show(this, "원본 이미지 파일이 존재하지 않습니다.", "확인", MessageBoxButtons.OK, MessageBoxIcon.Warning);
            return;
        }

        _statusLabel.Text = "Vision 검사 준비 완료";
    }

    private void OpenResolutionDialog()
    {
        using var dialog = new ResolutionForm(_resolutionX, _resolutionY);
        if (dialog.ShowDialog(this) != DialogResult.OK)
        {
            return;
        }

        _resolutionX = dialog.ResolutionX;
        _resolutionY = dialog.ResolutionY;
        _imageCanvas.SetResolution(_resolutionX, _resolutionY);
        MessageBox.Show(this, $"X값: {_resolutionX:F2}, Y값: {_resolutionY:F2}", "분해능 설정",
            MessageBoxButtons.OK, MessageBoxIcon.Information);
    }

    private void StartMeasureMode()
    {
        if (_currentBitmap is null)
        {
            MessageBox.Show(this, "이미지를 먼저 열어 주세요.", "거리 측정", MessageBoxButtons.OK, MessageBoxIcon.Information);
            return;
        }

        if (_resolutionX <= 0 || _resolutionY <= 0)
        {
            MessageBox.Show(this, "먼저 분해능을 설정해 주세요.", "거리 측정", MessageBoxButtons.OK, MessageBoxIcon.Information);
            return;
        }

        _imageCanvas.StartMeasureMode();
        _statusLabel.Text = "거리 측정 : 시작점을 클릭하세요.";
    }

    private void ClearMeasurements()
    {
        _imageCanvas.ClearMeasurements();
        _statusLabel.Text = "측정선을 지웠습니다.";
    }

    private void UpdateImageInfo()
    {
        if (_currentBitmap is null)
        {
            _fileValueLabel.Text = "-";
            _widthValueLabel.Text = "-";
            _heightValueLabel.Text = "-";
            _pixelsValueLabel.Text = "-";
            return;
        }

        var pixels = (long)_currentBitmap.Width * _currentBitmap.Height;
        _fileValueLabel.Text = Path.GetFileName(_currentFilePath);
        _widthValueLabel.Text = _currentBitmap.Width.ToString();
        _heightValueLabel.Text = _currentBitmap.Height.ToString();
        _pixelsValueLabel.Text = pixels.ToString();
    }

    private static GroupBox CreateInfoGroup(string title, IReadOnlyList<(string Name, Label Value)> rows)
    {
        var group = new GroupBox
        {
            Text = title,
            Dock = DockStyle.Top,
            AutoSize = true,
            Padding = new Padding(12)
        };

        var table = new TableLayoutPanel
        {
            Dock = DockStyle.Top,
            AutoSize = true,
            ColumnCount = 2
        };

        table.ColumnStyles.Add(new ColumnStyle(SizeType.Absolute, 80));
        table.ColumnStyles.Add(new ColumnStyle(SizeType.Percent, 100));

        foreach (var row in rows)
        {
            table.RowStyles.Add(new RowStyle(SizeType.AutoSize));
            table.Controls.Add(new Label { Text = $"{row.Name} :", AutoSize = true, Margin = new Padding(0, 4, 0, 4) });
            table.Controls.Add(row.Value);
        }

        group.Controls.Add(table);
        return group;
    }

    private static Button CreateButton(string text)
    {
        return new Button
        {
            Text = text,
            Width = 220,
            Height = 34,
            Margin = new Padding(0, 0, 0, 8)
        };
    }

    private static Label CreateValueLabel(string text = "-")
    {
        return new Label
        {
            Text = text,
            AutoSize = true,
            Margin = new Padding(0, 4, 0, 4)
        };
    }
}

internal sealed class ImageCanvas : ScrollableControl
{
    private readonly List<MeasureLine> _measureLines = new();
    private Bitmap? _image;
    private Point? _startPoint;
    private Point? _currentPoint;
    private bool _measureMode;
    private double _resolutionX = 50.0;
    private double _resolutionY = 30.0;
    private float _zoom = 1.0f;

    public event EventHandler<Point?>? PixelHovered;
    public event EventHandler<double>? MeasurementCompleted;

    public ImageCanvas()
    {
        Dock = DockStyle.Fill;
        AutoScroll = true;
        BackColor = Color.FromArgb(30, 30, 30);
        Cursor = Cursors.Cross;
        DoubleBuffered = true;
    }

    public float Zoom
    {
        get => _zoom;
        set
        {
            _zoom = Math.Max(0.01f, value);
            UpdateScrollSize();
            Invalidate();
        }
    }

    public void SetImage(Bitmap image)
    {
        _image = image;
        _measureLines.Clear();
        _startPoint = null;
        _currentPoint = null;
        UpdateScrollSize();
        Invalidate();
    }

    public void SetResolution(double resolutionX, double resolutionY)
    {
        _resolutionX = resolutionX;
        _resolutionY = resolutionY;
    }

    public void StartMeasureMode()
    {
        _measureMode = true;
        _startPoint = null;
        _currentPoint = null;
        Invalidate();
    }

    public void ClearMeasurements()
    {
        _measureLines.Clear();
        _startPoint = null;
        _currentPoint = null;
        Invalidate();
    }

    protected override void OnMouseMove(MouseEventArgs e)
    {
        base.OnMouseMove(e);

        var imagePoint = ClientToImage(e.Location);
        PixelHovered?.Invoke(this, imagePoint);

        if (_measureMode && _startPoint is not null && imagePoint is not null)
        {
            _currentPoint = imagePoint;
            Invalidate();
        }
    }

    protected override void OnMouseDown(MouseEventArgs e)
    {
        base.OnMouseDown(e);

        if (e.Button != MouseButtons.Left || !_measureMode)
        {
            return;
        }

        var imagePoint = ClientToImage(e.Location);
        if (imagePoint is null)
        {
            return;
        }

        if (_startPoint is null)
        {
            _startPoint = imagePoint.Value;
            _currentPoint = imagePoint.Value;
            Invalidate();
            return;
        }

        var distance = CalculateRealDistance(_startPoint.Value, imagePoint.Value);
        _measureLines.Add(new MeasureLine(_startPoint.Value, imagePoint.Value, distance));
        _startPoint = null;
        _currentPoint = null;
        MeasurementCompleted?.Invoke(this, distance);
        Invalidate();
    }

    protected override void OnPaint(PaintEventArgs e)
    {
        base.OnPaint(e);

        e.Graphics.SmoothingMode = SmoothingMode.AntiAlias;
        e.Graphics.Clear(BackColor);

        if (_image is null)
        {
            DrawEmptyMessage(e.Graphics);
            return;
        }

        var offset = AutoScrollPosition;
        e.Graphics.TranslateTransform(offset.X, offset.Y);
        e.Graphics.ScaleTransform(_zoom, _zoom);
        e.Graphics.InterpolationMode = InterpolationMode.NearestNeighbor;
        e.Graphics.PixelOffsetMode = PixelOffsetMode.Half;
        e.Graphics.DrawImage(_image, Point.Empty);

        using var pen = new Pen(Color.Red, 2 / _zoom);
        using var font = new Font(Font.FontFamily, Math.Max(8, 11 / _zoom), FontStyle.Bold);
        using var brush = new SolidBrush(Color.Red);

        foreach (var line in _measureLines)
        {
            DrawMeasureLine(e.Graphics, pen, font, brush, line);
        }

        if (_startPoint is not null && _currentPoint is not null)
        {
            e.Graphics.DrawLine(pen, _startPoint.Value, _currentPoint.Value);
        }
    }

    private void DrawMeasureLine(Graphics graphics, Pen pen, Font font, Brush brush, MeasureLine line)
    {
        graphics.DrawLine(pen, line.StartPoint, line.EndPoint);

        var textPoint = new PointF(
            (line.StartPoint.X + line.EndPoint.X) / 2f,
            (line.StartPoint.Y + line.EndPoint.Y) / 2f);

        graphics.DrawString($"{line.Distance:F2} um", font, brush, textPoint);
    }

    private void DrawEmptyMessage(Graphics graphics)
    {
        const string message = "이미지를 열어 주세요.";
        using var brush = new SolidBrush(Color.WhiteSmoke);
        var size = graphics.MeasureString(message, Font);
        graphics.DrawString(message, Font, brush, (Width - size.Width) / 2f, (Height - size.Height) / 2f);
    }

    private Point? ClientToImage(Point clientPoint)
    {
        if (_image is null)
        {
            return null;
        }

        var scroll = AutoScrollPosition;
        var imageX = (int)Math.Floor((clientPoint.X - scroll.X) / _zoom);
        var imageY = (int)Math.Floor((clientPoint.Y - scroll.Y) / _zoom);

        if (imageX < 0 || imageY < 0 || imageX >= _image.Width || imageY >= _image.Height)
        {
            return null;
        }

        return new Point(imageX, imageY);
    }

    private double CalculateRealDistance(Point start, Point end)
    {
        var deltaX = (end.X - start.X) * _resolutionX;
        var deltaY = (end.Y - start.Y) * _resolutionY;
        return Math.Sqrt((deltaX * deltaX) + (deltaY * deltaY));
    }

    private void UpdateScrollSize()
    {
        if (_image is null)
        {
            AutoScrollMinSize = Size.Empty;
            return;
        }

        AutoScrollMinSize = new Size(
            (int)Math.Ceiling(_image.Width * _zoom),
            (int)Math.Ceiling(_image.Height * _zoom));
    }

    private sealed record MeasureLine(Point StartPoint, Point EndPoint, double Distance);
}

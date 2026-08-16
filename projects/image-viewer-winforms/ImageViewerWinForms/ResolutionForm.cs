namespace ImageViewerWinForms;

internal sealed class ResolutionForm : Form
{
    private readonly TextBox _resolutionXTextBox = new();
    private readonly TextBox _resolutionYTextBox = new();

    public ResolutionForm(double resolutionX, double resolutionY)
    {
        ResolutionX = resolutionX;
        ResolutionY = resolutionY;

        BuildLayout();
        _resolutionXTextBox.Text = resolutionX.ToString("0.###");
        _resolutionYTextBox.Text = resolutionY.ToString("0.###");
    }

    public double ResolutionX { get; private set; }

    public double ResolutionY { get; private set; }

    private void BuildLayout()
    {
        Text = "분해능 설정";
        StartPosition = FormStartPosition.CenterParent;
        FormBorderStyle = FormBorderStyle.FixedDialog;
        MaximizeBox = false;
        MinimizeBox = false;
        ClientSize = new Size(360, 180);

        var table = new TableLayoutPanel
        {
            Dock = DockStyle.Fill,
            Padding = new Padding(20),
            ColumnCount = 2,
            RowCount = 3
        };

        table.ColumnStyles.Add(new ColumnStyle(SizeType.Absolute, 150));
        table.ColumnStyles.Add(new ColumnStyle(SizeType.Percent, 100));
        table.RowStyles.Add(new RowStyle(SizeType.AutoSize));
        table.RowStyles.Add(new RowStyle(SizeType.AutoSize));
        table.RowStyles.Add(new RowStyle(SizeType.Percent, 100));

        table.Controls.Add(new Label { Text = "분해능 X (um/pixel) :", AutoSize = true, Anchor = AnchorStyles.Left }, 0, 0);
        table.Controls.Add(_resolutionXTextBox, 1, 0);
        table.Controls.Add(new Label { Text = "분해능 Y (um/pixel) :", AutoSize = true, Anchor = AnchorStyles.Left }, 0, 1);
        table.Controls.Add(_resolutionYTextBox, 1, 1);

        var okButton = new Button { Text = "확인", DialogResult = DialogResult.None, Width = 80 };
        var cancelButton = new Button { Text = "취소", DialogResult = DialogResult.Cancel, Width = 80 };
        var buttonPanel = new FlowLayoutPanel
        {
            Dock = DockStyle.Bottom,
            FlowDirection = FlowDirection.RightToLeft,
            AutoSize = true
        };

        buttonPanel.Controls.Add(cancelButton);
        buttonPanel.Controls.Add(okButton);

        table.SetColumnSpan(buttonPanel, 2);
        table.Controls.Add(buttonPanel, 0, 2);

        Controls.Add(table);
        AcceptButton = okButton;
        CancelButton = cancelButton;

        okButton.Click += (_, _) => SaveResolution();
    }

    private void SaveResolution()
    {
        // 분해능은 거리 계산식에 직접 들어가므로 숫자와 양수 여부를 먼저 확인한다.
        if (!double.TryParse(_resolutionXTextBox.Text, out var resolutionX) || resolutionX <= 0)
        {
            MessageBox.Show(this, "분해능 X 값을 0보다 큰 숫자로 입력해 주세요.", "입력 오류",
                MessageBoxButtons.OK, MessageBoxIcon.Warning);
            _resolutionXTextBox.Focus();
            return;
        }

        if (!double.TryParse(_resolutionYTextBox.Text, out var resolutionY) || resolutionY <= 0)
        {
            MessageBox.Show(this, "분해능 Y 값을 0보다 큰 숫자로 입력해 주세요.", "입력 오류",
                MessageBoxButtons.OK, MessageBoxIcon.Warning);
            _resolutionYTextBox.Focus();
            return;
        }

        ResolutionX = resolutionX;
        ResolutionY = resolutionY;
        DialogResult = DialogResult.OK;
        Close();
    }
}

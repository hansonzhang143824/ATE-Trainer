// Altium Designer Script: ExportFullNetlist.pas
// 遍历所有原理图，导出 Port 类型、Net 名称、元件 Pin 连接等全部信息
// 用法: AD → File → Run Script → 选 ExportFullNetlist → Run

procedure ExportFullNetlist;
var
    Doc       : ISch_Document;
    SchDoc    : ISch_Document;
    Iterator  : ISch_Iterator;
    Sheet     : ISch_Sheet;
    Port      : ISch_Port;
    NetLabel  : ISch_NetLabel;
    Component : ISch_Component;
    Pin       : ISch_Pin;
    Wire      : ISch_Wire;
    Bus       : ISch_Bus;
    BusEntry  : ISch_BusEntry;
    NetItem   : ISch_GraphicalObject;
    OutputPath: String;
    F         : TextFile;
    I, J      : Integer;
    SheetList : TList;
    SheetName : String;
    NetName   : String;
    PortName  : String;
    CompName  : String;
    PinNum    : String;
    PinName   : String;
    FileName  : String;

    // 辅助: 从物理连接获取 net 名 (AD 的 pin/net 关联通过物理连接对象)
    function GetNetNameAtLocation(SchDoc: ISch_Document; X, Y: TCoord): String;
    var
        SpatialIter: ISch_Iterator;
        Obj        : ISch_GraphicalObject;
        NetObj     : ISch_Net;
    begin
        Result := '';
        SpatialIter := SchDoc.SchIterator_Create;
        SpatialIter.SetState_IterationDepth(eIterateAllLayers);
        SpatialIter.AddFilter_ObjectSet(MkSet(eSchNetLabel, eSchPort, eSchWire, eSchBus, eSchBusEntry));
        Obj := SpatialIter.FindClosestToXY(eHitTest_All, X, Y);
        if Obj <> nil then
        begin
            if Obj.ObjectId = eWire then
                Result := Obj.Net;
            if Result = '' then
            begin
                // Walk connected objects to find a net label
                NetObj := Obj.GetState_Net;
                if NetObj <> nil then
                    Result := NetObj.GetState_NetName;
            end;
        end;
        SchDoc.SchIterator_Destroy(SpatialIter);
    end;

begin
    // 输出路径
    OutputPath := ExtractFilePath(CurrentProject.Document.DocumentName);
    if OutputPath = '' then
        OutputPath := 'D:\';

    FileName := OutputPath + ChangeFileExt(ExtractFileName(CurrentProject.Document.DocumentName), '') + '_FullNetlist.txt';
    AssignFile(F, FileName);
    Rewrite(F);

    WriteLn(F, '========================================');
    WriteLn(F, 'AD Full Netlist Export');
    WriteLn(F, 'Project: ' + CurrentProject.Document.DocumentName);
    WriteLn(F, 'Date: ' + DateTimeToStr(Now));
    WriteLn(F, '========================================');
    WriteLn(F, '');

    // 遍历每张原理图
    for I := 0 to CurrentProject.DocumentCount - 1 do
    begin
        Doc := CurrentProject.Documents[I];
        if Doc.DocumentName = '' then Continue;
        if Pos('.SchDoc', Doc.DocumentName) = 0 then Continue;

        SchDoc := Doc;
        SheetName := SchDoc.DocumentName;

        WriteLn(F, '========================================');
        WriteLn(F, 'Sheet: ' + SheetName);
        WriteLn(F, '========================================');

        // ===== 1. 导出所有 Port =====
        WriteLn(F, '--- PORTS ---');
        Iterator := SchDoc.SchIterator_Create;
        Iterator.AddFilter_ObjectSet(MkSet(ePort));
        Port := Iterator.FirstSchObject;
        while Port <> nil do
        begin
            WriteLn(F, Format('PORT|%s|%s|IOType=%s|Style=%s|X=%d|Y=%d|Sheet=%s',
                [Port.Name,
                 Port.Text,
                 Port.GetState_IOType,
                 Port.GetState_Style,
                 Port.Location.X,
                 Port.Location.Y,
                 SheetName]));
            Port := Iterator.NextSchObject;
        end;
        SchDoc.SchIterator_Destroy(Iterator);

        // ===== 2. 导出所有 NetLabel =====
        WriteLn(F, '--- NET LABELS ---');
        Iterator := SchDoc.SchIterator_Create;
        Iterator.AddFilter_ObjectSet(MkSet(eNetLabel));
        NetLabel := Iterator.FirstSchObject;
        while NetLabel <> nil do
        begin
            WriteLn(F, Format('NETLABEL|%s|X=%d|Y=%d|Sheet=%s',
                [NetLabel.Text,
                 NetLabel.Location.X,
                 NetLabel.Location.Y,
                 SheetName]));
            NetLabel := Iterator.NextSchObject;
        end;
        SchDoc.SchIterator_Destroy(Iterator);

        // ===== 3. 导出所有 Component 及 Pin =====
        WriteLn(F, '--- COMPONENTS ---');
        Iterator := SchDoc.SchIterator_Create;
        Iterator.AddFilter_ObjectSet(MkSet(eSchComponent));
        Component := Iterator.FirstSchObject;
        while Component <> nil do
        begin
            // 跳过电源端口等虚拟器件
            CompName := Component.Designator.Text;
            if CompName = '' then
                CompName := Component.UniqueId;

            WriteLn(F, Format('COMP|%s|Part=%s|Lib=%s|Sheet=%s',
                [CompName,
                 Component.PartCount,
                 Component.LibReference,
                 SheetName]));

            // 导出每个 Pin
            for J := 0 to Component.PinCount - 1 do
            begin
                Pin := Component.Pins[J];
                if Pin <> nil then
                begin
                    // AD 中 Pin 的 net 通过 GetState_NetName 获取
                    NetName := Pin.GetState_NetName;
                    if NetName = '' then
                        NetName := '(unconnected)';

                    WriteLn(F, Format('  PIN|%s|%s|Designator=%s|Net=%s|Electrical=%s',
                        [CompName,
                         Pin.Name,
                         Pin.Designator,
                         NetName,
                         Pin.Electrical]));
                end;
            end;

            Component := Iterator.NextSchObject;
        end;
        SchDoc.SchIterator_Destroy(Iterator);

        // ===== 4. 导出所有 Net (通过物理连接) =====
        WriteLn(F, '--- NETS (from physical connectivity) ---');
        Iterator := SchDoc.SchIterator_Create;
        Iterator.AddFilter_ObjectSet(MkSet(eWire, eBus, eBusEntry));
        Wire := Iterator.FirstSchObject;
        while Wire <> nil do
        begin
            NetName := Wire.Net;
            if NetName <> '' then
            begin
                WriteLn(F, Format('NET|%s|X=%d|Y=%d|Sheet=%s',
                    [NetName,
                     Wire.Location.X,
                     Wire.Location.Y,
                     SheetName]));
            end;
            Wire := Iterator.NextSchObject;
        end;
        SchDoc.SchIterator_Destroy(Iterator);

        WriteLn(F, '');
    end;

    // ===== 5. 项目级 Net 连通性 (Inter-sheet connections) =====
    WriteLn(F, '========================================');
    WriteLn(F, 'PROJECT-LEVEL NETS (Physical Connectivity)');
    WriteLn(F, '========================================');

    // 遍历所有物理 Net
    for I := 0 to CurrentProject.DocumentCount - 1 do
    begin
        Doc := CurrentProject.Documents[I];
        if Doc.DocumentName = '' then Continue;
        if Pos('.SchDoc', Doc.DocumentName) = 0 then Continue;

        SchDoc := Doc;
        SheetName := SchDoc.DocumentName;

        Iterator := SchDoc.SchIterator_Create;
        Iterator.AddFilter_ObjectSet(MkSet(eSchPort));
        Port := Iterator.FirstSchObject;
        while Port <> nil do
        begin
            PortName := Port.Name;
            NetName := Port.Net;
            if NetName <> '' then
            begin
                WriteLn(F, Format('INTERSHEET|Port=%s|Net=%s|IOType=%s|Sheet=%s',
                    [PortName,
                     NetName,
                     Port.GetState_IOType,
                     SheetName]));
            end;
            Port := Iterator.NextSchObject;
        end;
        SchDoc.SchIterator_Destroy(Iterator);
    end;

    CloseFile(F);
    ShowMessage('Export done!' + #13#10 + 'File: ' + FileName);
end;

// 主入口
begin
    ExportFullNetlist;
end.

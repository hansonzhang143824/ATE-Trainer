// ExportCurrentSheet.pas — AD 19 verified
// 打开一张 .SchDoc → Run Script → ExportCurrentSheet

procedure ExportCurrentSheet;
var
    Doc  : ISch_Document;
    Iter : ISch_Iterator;
    O    : ISch_GraphicalObject;
    C    : ISch_Component;
    P    : ISch_Pin;
    J, PN : Integer;
    Desig, LibRef, Net, PortName, PortIO, LabelText : String;
    Path, FN: String;
    F    : TextFile;
begin
    Doc := SchServer.GetCurrentSchDocument;
    if Doc = nil then begin ShowMessage('Open a .SchDoc first!'); Exit; end;
    Path := ExtractFilePath(Doc.DocumentName);
    if Path = '' then Path := 'D:\';
    FN := Path + ChangeFileExt(ExtractFileName(Doc.DocumentName), '') + '_' + IntToStr(Round(Now * 86400)) + '_Netlist.txt';
    AssignFile(F, FN); Rewrite(F);
    WriteLn(F, '=== ' + Doc.DocumentName + ' ===');

    // Ports
    WriteLn(F, '--- PORTS ---');
    Iter := Doc.SchIterator_Create;
    Iter.AddFilter_ObjectSet(MkSet(ePort));
    O := Iter.FirstSchObject;
    while O <> nil do begin
        PortName := O.Name;
        PortIO   := IntToStr(O.IOType);
        Net      := O.Net;
        WriteLn(F, 'PORT|' + PortName + '|IO=' + PortIO + '|Net=' + Net);
        O := Iter.NextSchObject;
    end;
    Doc.SchIterator_Destroy(Iter);

    // Net Labels
    WriteLn(F, '--- NETLABELS ---');
    Iter := Doc.SchIterator_Create;
    Iter.AddFilter_ObjectSet(MkSet(eNetLabel));
    O := Iter.FirstSchObject;
    while O <> nil do begin
        LabelText := O.Text;
        Net       := O.Net;
        WriteLn(F, 'NETLABEL|' + LabelText + '|Net=' + Net);
        O := Iter.NextSchObject;
    end;
    Doc.SchIterator_Destroy(Iter);

    // Power Ports
    WriteLn(F, '--- POWER ---');
    Iter := Doc.SchIterator_Create;
    Iter.AddFilter_ObjectSet(MkSet(ePowerObject));
    O := Iter.FirstSchObject;
    while O <> nil do begin
        WriteLn(F, 'POWER|' + O.Text + '|Net=' + O.Net);
        O := Iter.NextSchObject;
    end;
    Doc.SchIterator_Destroy(Iter);

    // Components + Pins
    WriteLn(F, '--- COMPONENTS ---');
    Iter := Doc.SchIterator_Create;
    Iter.AddFilter_ObjectSet(MkSet(eSchComponent));
    C := Iter.FirstSchObject;
    while C <> nil do begin
        Desig  := C.Designator.Text;
        LibRef := C.LibReference;
        WriteLn(F, 'COMP|' + Desig + '|' + LibRef);
        PN := C.PinCount;
        for J := 0 to PN - 1 do begin
            P := C.Pins[J];
            if P <> nil then begin
                Net := P.Net;
                if Net = '' then Net := '(NC)';
                WriteLn(F, '  PIN|' + P.Name + '|' + P.Designator + '|' + Net);
            end;
        end;
        C := Iter.NextSchObject;
    end;
    Doc.SchIterator_Destroy(Iter);

    // Sheet Entries (跨页连接)
    WriteLn(F, '--- SHEET ENTRIES ---');
    Iter := Doc.SchIterator_Create;
    Iter.AddFilter_ObjectSet(MkSet(eSheetEntry));
    O := Iter.FirstSchObject;
    while O <> nil do begin
        WriteLn(F, 'SHEETENTRY|' + O.Name + '|IO=' + IntToStr(O.IOType) + '|Net=' + O.Net);
        O := Iter.NextSchObject;
    end;
    Doc.SchIterator_Destroy(Iter);

    CloseFile(F);
    ShowMessage('OK: ' + FN);
end;
